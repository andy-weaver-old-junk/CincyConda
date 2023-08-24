import sys
import os
import subprocess
from collections import namedtuple
from typing import List, Union, Optional, Tuple, Dict, Any
import pandas as pd

from get_tech_contacts import get_tech_contacts

CONDA_INSTALL_PATH = "/rsystem/Rapps/anaconda310/bin/conda"

class CincyConda:
    def __init__(self,
                 packages: list = None,
                 conda_install_path: str = CONDA_INSTALL_PATH,
                 shell: str = 'bash',
                 channel_alias: str = None,
                 name: str = ".env",
                 path: str = "./.env/",
                 ):
        self.packages = packages
        self.conda = conda_install_path
        self.shell = shell
        self.channel_alias = channel_alias
        self.name = name
        self.path = path

        # set the tech contacts
        self.tech_contacts = get_tech_contacts()

        self.conda_envs = None

    def __post_init__(self):
        # if the base env is not activated, activate it
        self._activate_base()

        # if jupyter, notebook, ipykernel are not passed in, add them
        if 'jupyter' not in self.packages:
            self.packages.append('jupyter')
        if 'notebook' not in self.packages:
            self.packages.append('notebook')
        if 'ipykernel' not in self.packages:
            self.packages.append('ipykernel')

    def __str__(self):
        return f"CincyConda({self.name})"

    def __repr__(self):
        return f"CincyConda({self.name})"

    def Help(self, search_term: str = None) -> None:
        """
        Prints documentation for the CondaEnv class to the console, including a list of methods.
        If a search term is provided, only prints the docstring for that method.

        Parameters
        ----------
        search_term : str, optional
            A search term to search the docstrings for, by default None

        Returns
        -------
        None. Prints documentation to the console.
        """
        # get the docstring
        doc = get_docstring()

        # if no search term is provided, print the docstring
        if search_term is None:
            print(doc)

        # if a search term is provided, print the docstring for that method
        else:
            # get the docstring for the method
            doc = doc.split(f"def {search_term}")[1].split('"""')[1]

            # print the docstring
            print(doc)

    def Setup(self):
        """
        Does the unique setup steps for setting up anaconda on the jupyterhub server.
        """
        # initialize conda in the user's shell
        self.init(help=False)

        # close and re-open the shell
        subprocess.run([f'{self.shell}', '-c', 'exit'])

        # list the commands to run
        cmd = [
            # clear the conda cache and channel list
            f"{self.conda} clean --all",

            # add the CIC repo
            f"{self.conda} config --set channel_alias {self.channel_alias}/repo",

            # add the restricted_channel to default channels
            f"{self.conda} config --prepend channels default_channels restricted_channel",

            # add the CIC repo to the default channels
            f"{self.conda} repo config --set sites.anaconda.url {self.channel_alias}",

            # set anaconda to be the default site
            f"{self.conda} repo config --set default_site anaconda",

            # log in
            f"{self.conda} repo login"
        ]

        # loop through the commands and run them
        for c in cmd:
            subprocess.run(c.split())

    def Init(self,
             help: bool = False) -> None:
        """
        Initializes conda in the user's shell

        Parameters
        ----------
        shell : str, optional
            The shell to initialize conda in, by default 'bash'
        help : bool, optional
            Whether to print the help message, by default False

        Returns
        -------
        None. Initializes conda in the user's shell.

        

        Raises
        # check the shell input
        assert self.shell in ['bash', 'zsh', 'fish', 'powershell', 'xonsh'], \
            f"shell: '{self.shell}' is not supported. Please use one of the following: \
             ['bash', 'zsh', 'fish', 'powershell', 'xonsh']"

        if help:
            msg = os.system(f"{self.conda} init --help")
        else:
            # initialize conda in the user's shell
            msg = os.system(f"{self.conda} init {self.shell}")

        print(msg)

    def Create(self,
               packages: list = None,
               help:bool = False) -> None:
        # check to see whether or not an env already exists at self.path
        assert not os.path.exists(self.path), \
            f"An environment already exists at {self.path}. Please either use this env, or \
delete it and create a new one."
        if packages is None and self.packages is not None:
            packages = self.packages
        elif packages is not None and self.packages is None:
            packages = packages
        else:
            packages = []

        # loop through the packages and check that they are in the CincyPy channel
        for package in packages:
            # get the packages in the CincyPy channel
            packages = self._get_packages_in_channel()

            # get the list of missing packages
            missing_packages = [package for package in packages if package not in packages]

            # check if the package is in the CincyPy channel
            assert len(missing_packages) == 0, \
                f"Package: {', '.join([p for p in missing_packages])} is not in the \
CincyPy channel. Please use a package from the CincyPy channel, or submit a request \
to add the package to the CincyPy channel using the Request method."


        # create the env with name=self.name and path=self.path
        os.system(f"{self.conda} create --prefix {self.path} -y")

        # create the kernel
        os.system(f"python -m ipykernel install --user --name {self.name} \
--display-name {self.name}")

        # if the base env is not activated, activate it
        self._activate_base()

    def Remove(self,
               env:str = None,
               package:str = None,
               help:bool = False):
        """
        Removes a CinycConda environment from the system. Cannot be used to remove
        the base environment.
        """
        if help:
            msg = os.system(f"{self.conda} env remove --help")
        else:
                
            # make sure the env is not the base env
            assert env.name.lower() != 'base', \
                "CincyConda cannot be used to remove the base environment."

            # make sure the env is not the current env
            assert env.name.lower() != self.name.lower(), \
                f"Cannot remove the current environment: {self.name}"

            # make sure the env is in the list of envs
            assert env in self.env(), \
                f"Could not find environment: {env}. Please use one of the following: \
{self.env()}"

            # remove the env
            subprocess.run([f"{self.conda}", "env", "remove",
                            "--name", f"{env.name}", "-y"])

    def update(self, package):
        # if the base env is not activated, activate it
        self._activate_base()

        # update the env
        os.system(f"{self.conda} update --prefix {self.path} {package} -y")

        # if the base env is not activated, activate it
        self._activate_base()

    def _activate_env(self,
                      env:str = "base") -> None:
        """
        This is a helper function used in the `Activate` method. It activates the
        environment indicated by `env`. If no environment is provided, the base
        environment is activated.

        It is not intended to be used directly.

        Parameters
        ----------
        env : str, optional
            The name of the environment to activate, by default "base"

        Returns
        -------
        None. Activates the environment indicated by env, prints a message to the console.
        """
        if env=="base":
            os.system("conda activate base")
            print("Activated base environment")
        else:
            os.system(f"conda activate {env}")
            print(f"Activated environment: {env}")

    def Activate(self, env:str = 'base'):
        """
        Activates a CincyConda environment. If no environment is provided, the base
        environment is activated.
        """
        assert hasattr(self, 'conda'), \
            f"conda_install_path is not set. Please set it to the path of your conda \
installation. Try '{CONDA_INSTALL_PATH}'"
        assert hasattr(sys, 'base_prefix'), \
f"sys.base_prefix: '{sys.base_prefix}' is not set"

        # activate the env indicated by env, or the base env if no env is provided
        if env == 'base':
            self._activate_env('base')
        else:
            # check that the env exists, and if it does, activate it
            try:
                assert self.env(env) is not None, \
                    f"""Could not find environment: {env}. Please use one of the \
following: 
{self.env()}"""
                self._activate_env(env)

            # if the env does not exist, print an error message and
            # activate the base env as a fallback
            except AssertionError as e:
                print(e)
                self._activate_env('base')

    def Install(self,
                env:str = None,
                package:str = None,
                help:bool = False):
        """
        Installs a package into the current environment. If no package is provided,
        nothing happens.

        Parameters
        ----------
        env : str, optional
            The name of the environment to install the package into, by
            default None. If no environment is provided, the package is installed
            into the current environment.
        package : str, optional
            The name of the package to install, by default None
        help : bool, optional
            Whether to print the help message, by default False

        Returns
        -------
        None. Installs the package into the current environment.

        Raises
        ------
        AssertionError
            If the package is not a string
        AssertionError
            If the package is not in the CincyPy channel

        Example Usage
        -------------
        >>> from CincyConda import CincyConda
        >>> env = CincyConda(name='test', packages=['numpy', 'pandas'])
        >>> env.Install(package='numpy')

        >>> # expected output:
        >>> # Collecting package metadata (current_repodata.json): done
        >>> # Solving environment: done
        >>> #
        >>> # # All requested packages already installed.
        """
        assert env != 'base', \
            "CincyConda cannot be used to install packages into the base environment."

        # if an env is not provided, install the package into the current env, 
        # unless the current env is the base env
        assert env is not None and env != 'base', \
            "CincyConda cannot be used to install packages into the base environment. \
The current environment is the base environment, so please either activate a different \
environment, or pass in an environment name to the Install method."

        # if no package is provided, return
        if package is None:
            print("No package provided. Nothing to install.")
            return

        # install the package
        subprocess.run([f"{self.conda}", "install", "--prefix", f"{self.path}",
                        "-y", f"{package}"])

        # if the base env is not activated, activate it
        self._activate_base()

    def _all_envs(self) -> list:
        """
        Returns the available conda environments in a python list

        Parameters
        ----------
        name : str
            The name of the conda environment to return

        Returns
        -------
        list
            A list of available conda environments

        Raises
        ------
        AssertionError
            If the name is not a string
        AssertionError
            If the name is not in the list of available conda environments, and is
            not a substring of any of the available conda environment names or paths

        """
        # get the envs
        # envs = os.system(f"{self.conda} env list")

        if self.conda_envs is not None:
            return self.conda_envs
        else:
            envs = subprocess.run([f"{self.conda}", "env", "list"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

            # convert to a list
            if envs.returncode != 0:
                print(f"Error executing command: {envs.stderr.decode('utf-8')}")
                return []
            else:
                self.conda_envs = namedtuple('CondaEnv', ['name', 'path'])   
                output = []
                for line in envs.stdout.decode('utf-8').splitlines()[2:]:
                    env_name = line.split()
                    env_path = line.split()
                    output.append(self.conda_envs(env_name, env_path))
            self.conda_envs = output
            return output

    

    def Env(self,
            name:str = None,
            help:bool = False) -> Union[list, str]:
        """
        Returns the available conda environments in a python list

        Parameters
        ----------
        name : str
            The name of the conda environment to return
        help : bool, optional
            Whether to print the help message, by default False

        Returns
        -------
        list
            A list of available conda environments
        
        Raises
        ------
        AssertionError
            If the name is not a string
        AssertionError
            If the name is not in the list of available conda environments, and is
            not a substring of any of the available conda environment names or paths

        """
        # get the envs
        envs = self._all_envs()

        # if no name is provided, return all envs
        if name is None:
            return envs

        # if a name is provided, make sure it is a string
        assert isinstance(name, str), \
            f"name must be a string, not {type(name)}"
        
        # if the name is in the list of CincyConda objects, return it
        if name in [env.name for env in envs]:
            return [env for env in envs if env.name == name][0]
        
        # if the name is not in the list of CincyConda objects, check if it is a substring
        # of any of the names first, then the paths
        elif name not in [env.name for env in envs]:
            envs = [env for env in envs if name in env.name]
            if len(envs) == 1:
                return envs[0]
            elif len(envs) > 1:
                return envs
            else:
                envs = [env for env in envs if name in env.path]
                if len(envs) == 1:
                    return envs[0]
                elif len(envs) > 1:
                    return envs
                else:
                    raise AssertionError(f"Could not find environment: {name}")

    def Request(self, package:str = None):
        """
        Creates a request to add a package to the CincyPy channel. If no package is provided,
        nothing happens. Otherwise, the user is prompted to provide a reason for the request. 
        
        The package string is checked to make sure it is a valid package name, which in this
        case means that it is hosted on PyPI. For example, the pandas library is hosted at:
            https://pypi.org/project/pandas/
        You should expect the URL to be formatted this way:
            https://pypi.org/project/{package}/
        Then the package string should be the same as the {package} part of the URL.

        Assuming the package is hosted on PyPI, the request is made by adding the user, date,
        package, reason, and status to the requests.csv file in the CincyPy channel. The status
        is set to 'unseen' by default.
        """
        # if no package is provided, return
        if package is None:
            return

        # check that the package is hosted on PyPI
        # get the list of packages hosted on PyPI
        is_on_pypi = self._is_packages_on_pypi(package)

        # check that the package is in the list of packages hosted on PyPI
        assert is_on_pypi, \
            f"Package: '{package}' is not hosted on PyPI. Please use a package hosted on PyPI, \
or contact one of {self.tech_contacts} for a custom package."