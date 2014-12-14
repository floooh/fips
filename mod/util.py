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

#-------------------------------------------------------------------------------
def get_build_dir(fips_dir) :
    """get absolute path to build directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :returns:           absolute path of build directory
    """
    return get_workspace_dir(fips_dir) + '/fips-build'

#-------------------------------------------------------------------------------
def get_deploy_dir(fips_dir) :
    """get absolute path to deploy directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :returns:           absolute path of deploy directory
    """
    return get_workspace_dir(fips_dir) + '/fips-deploy'

#-------------------------------------------------------------------------------
def get_project_name_from_url(url) :
    """get the project name from a git url

    :param url:     a git url
    :returns:       project name (last component of git url, minus extension)
    """
    return os.path.splitext(url.split('/')[-1])[0]

