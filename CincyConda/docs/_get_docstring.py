package_docstring="""CincyConda is a Python package that provides Python class
wrappers for the Conda package manager. It is designed to be used in conjunction 
with the CincyPy Conda channel, which provides pre-built packages for the CincyPy
community.

A typical use case for CincyConda is to create a Conda environment for a project
before installing packages. This can be done with the following code:


"""

init_docstring="""
        Initializes conda in the user's shell

        Parameters
        ----------
        shell : str, optional
            The shell to initialize conda in, by default 'bash'
        help : bool, optional
            Whether to print the help message, by default False

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If the shell is not supported

        Example Usage
        -------------
        >>> from CincyConda import CincyConda
        >>> env = CincyConda(name='test', packages=['numpy', 'pandas'])
        >>> env.init(shell='bash')
        
        >>> # expected output:
        >>> #  ==> For changes to take effect, close and re-open your current shell. <==
        >>> #  ==> If you'd prefer that conda's base environment not be activated on startup,
        >>> #      set the auto_activate_base parameter to false: <==
        >>> #  conda config --set auto_activate_base false
        """