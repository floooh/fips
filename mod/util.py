"""various utility functions"""

import os.path
import sys
import platform
import yaml
from mod import log

host_platforms = {
    'Darwin':   'osx',
    'Linux':    'linux',
    'Windows':  'win'
}

#-------------------------------------------------------------------------------
def fix_path(path) :
    """if on Windows, replace backslashes in path with forward slashes

    :param path:    input path
    :returns:       fixed up path
    """
    return path.replace('\\', '/')

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
def get_deploy_dir(fips_dir, proj_name, cfg) :
    """get absolute path to deploy directory in same workspace as fips

    :param fips_dir:    absolute path of fips
    :param proj_name:   project name
    :param cfg:         config object
    :returns:           absolute path of deploy directory
    """
    return '{}/fips-deploy/{}/{}'.format(get_workspace_dir(fips_dir), proj_name, cfg['name'])

#-------------------------------------------------------------------------------
def get_giturl_from_url(url) :
    """extracts the actual git url from an url string
    (splits off the branch name after the optional '#')

    :param url:     an url string, with optional '#' branch name appended
    :returns:       the actual git url
    """
    return url.split('#')[0]

#-------------------------------------------------------------------------------
def get_gitbranch_from_url(url) :
    """extracts the branch name from an url string
    (after the optional '#'), returns 'master' if no branch name
    specified.

    :param url:     an url string, with optional '#' branch name appended
    :returns:       the extracted branch name, or 'master'
    """
    if '#' in url :
        return url.split('#')[1]
    else :
        return 'master'

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
def lookup_target_cwd(proj_dir, target) :
    """lookup optional working directory for target from fips.yml,
    return None if no cwd has been specified for this target in fips.yml

    :param proj_dir:    absolute project directory
    :param target:      target name
    :returns:           working directory or None
    """
    target_cwd = None
    dic = load_fips_yml(proj_dir)
    if 'run' in dic :
        if target in dic['run'] :
            if 'cwd' in dic['run'][target] :
                target_cwd = proj_dir + '/' + dic['run'][target]['cwd']
    return target_cwd

#-------------------------------------------------------------------------------
def is_valid_project_dir(proj_dir) :
    """test if the provided directory is a valid fips project (has a
    fips.yml file)

    :param proj_dir:    absolute project directory to check
    :returns:           True if a valid fips project
    """
    if os.path.isdir(proj_dir) :
        if not os.path.isfile(proj_dir + '/fips.yml') :
            return False
        return True
    else :
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
    # we simply check whether the 'naked' url ends with '.git'
    url = get_giturl_from_url(url)
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

#-------------------------------------------------------------------------------
def get_host_platform() :
    """get the current host platform name (osx, linux or win)

    :returns: platform name (osx, linux, win)
    """
    return host_platforms[platform.system()]


