"""various utility functions"""

import os.path
import sys
import yaml
from mod import log

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
    return '{}/.fips-build/{}/{}'.format(get_workspace_dir(fips_dir), proj_name, cfg['name'])

#-------------------------------------------------------------------------------
def get_deploy_dir(fips_dir, proj_name, cfg) :
    """get absolute path to deploy directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :param proj_name:   project name
    :param cfg:         config object
    :returns:           absolute path of deploy directory
    """
    return '{}/.fips-deploy/{}/{}'.format(get_workspace_dir(fips_dir), proj_name, cfg['name'])

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

#-------------------------------------------------------------------------------
def load_fips_yml(proj_dir) :
    """load the fips.yml file from project directory

    :param proj_dir:    absolute project directory
    :returns:           dictionary object
    """
    dic = None
    path = proj_dir + '/fips.yml'
    if os.path.isfile(path) :
        with open(path, 'r') as f:
            dic = yaml.load(f)
    if not dic :
        dic = {}
    return dic

#-------------------------------------------------------------------------------
def is_valid_project_dir(proj_dir) :
    """test if the provided directory is a valid fips project (has a
    fips.yml and a fips file)

    :param proj_dir:    absolute project directory to check
    :returns:           True if a valid fips project
    """
    if os.path.isdir(proj_dir) :
        if not os.path.isfile(proj_dir + '/fips') :
            log.warn("no file 'fips' in project dir '{}'".format(proj_dir))
            return False
        if not os.path.isfile(proj_dir + '/fips.yml') :
            log.warn("no file 'fips.yml' in project dir '{}'".format(proj_dir))
            return False
        return True
    else :
        log.warn("project dir '{}' does not exist".format(proj_dir))
        return False

#-------------------------------------------------------------------------------
def ensure_valid_project_dir(proj_dir) :
    """test if project dir is valid, if not, dump error and abort

    :param proj_dir:    absolute project directory to check
    """
    if not is_valid_project_dir(proj_dir) :
        log.error("'{}' is not a valid project directory".format(proj_dir))

#-------------------------------------------------------------------------------
def is_git_url(url) :
    """check if 'url' is a valid git url

    :param url:     url string
    :returns:       True if a valid url
    """
    # we simply check whether the url ends with '.git'
    return url[-4:] == '.git'

#-------------------------------------------------------------------------------
def confirm(question) :
    """ask user to confirm (y/N)

    :param question:    the question to confirm
    :return:            True: user pressed 'y', False: user pressed 'n'
    """
    validAnswers={'': False, 'yes': True, 'ye': True, 'y': True, 'no': False, 'n': False }
    while True :
        sys.stdout.write(question + ' [y/N]: ')
        choice = raw_input().lower()
        if choice in validAnswers :
            return validAnswers[choice]
        else :
            log.info("please respond with 'y', 'yes', 'n' or 'no'")

#-------------------------------------------------------------------------------
def url_download_hook(count, block_size, total_size) :
    """a download progress hook for urllib"""
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write('\r{}%'.format(percent))

