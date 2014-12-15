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
def get_project_dir(fips_dir, proj_name) :
    """get absolute path to project directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :param proj_name:   project name
    :returns:           absolute path to project in same directory as fips
    """
    return get_workspace_dir(fips_dir) + '/' + proj_name

#-------------------------------------------------------------------------------
def get_build_dir(fips_dir, proj_name, cfg) :
    """get absolute path to build directory in same workspace as fips for 
    given configuration

    :param fips_dir:    absolute path of fips
    :param proj_name:   project name
    :param cfg:         config object
    :returns:           absolute path of build directory
    """
    return '{}/fips-build/{}/{}'.format(get_workspace_dir(fips_dir), proj_name, cfg['name'])

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

#-------------------------------------------------------------------------------
def get_project_name_from_dir(proj_dir) :
    """extract the project name from the absolute project directory

    :param proj_dir:    absolute project directory
    :returns:           project name (last dir-name of project directory)
    """
    return os.path.split(proj_dir)[1]
