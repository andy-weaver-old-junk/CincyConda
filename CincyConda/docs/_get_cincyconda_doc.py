def _str_wrapper(string:str):
    return f"""

======== CINCYCONDA DOCS ===========================================================================
            {string}
======== /CINCYCONDA DOCS ==========================================================================
"""

def _init_str(conda, shell):
    s = f"""
    
This method initializes conda in the user's shell. It is equivalent to running:
{self.conda} init {shell}

Parameters
----------
    shell : str, optional
        The shell to initialize conda in, by default 'bash'
    help : bool, optional
        Whether to print the help message, by default False

Returns
-------
    None. Prints the help message if help=True, otherwise prints the output of the command

Raises
------
    AssertionError
        If the shell is not supported

Example Usage
-------------
    >>> from CincyConda import CondaEnv
    >>> env = CondaEnv(name='test', packages=['numpy', 'pandas'])
    >>> env.init(shell='bash')

    >>> # expected output:
    >>> #  ==> For changes to take effect, close and re-open your current shell. <==
    >>> #  ==> If you'd prefer that conda's base environment not be activated on startup,
    >>> #      set the auto_activate_base parameter to false: <==
    >>> #  conda config --set auto_activate_base false   
    """
    return s

def get_wrapper(string, use_wrapper):
    if use_wrapper:
        return _str_wrapper(string)
    else:
        return string

def get_docstring(method:str,
                  conda:str='conda',
                  shell:str='bash',
                  use_wrapper:bool=True):
    """Get the docstring for a method of the CondaEnv class

    Parameters
    ----------
    method : str
        The name of the method to get the docstring for
    conda : str, optional
        The name of the conda executable, by default 'conda'
    shell : str, optional
        The shell to initialize conda in, by default 'bash'
    use_wrapper : bool, optional
        Whether to wrap the docstring in a header and footer, by default True

    Returns
    -------
    str
        The docstring for the method
    """
    def string_wrapper(string, use_wrapper=use_wrapper):
        return get_wrapper(string, use_wrapper=use_wrapper)

    if method == 'init':
        return string_wrapper(_init_str(conda='conda', shell='bash'))
    else:
        return None
