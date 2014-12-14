"""various utility functions"""

import os.path

#-------------------------------------------------------------------------------
def get_workspace_dir(fips_dir) :
    """get workspace (parent) dir from fips dir
    
    :param fips_dir:    absolute path to fips
    :returns:           absolute path to workspace (parent dir of fips)
    """
    return os.path.split(fips_dir)[0]

#-------------------------------------------------------------------------------
def get_project_dir(fips_dir, name) :
    """get absolute path to project directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :param name:        project name
    :returns:           absolute path to project in same directory as fips
    """
    return get_workspace_dir(fips_dir) + '/' + name
