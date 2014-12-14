"""project related functions"""

import os
import shutil

from mod import log, util
from mod.tools import git

#-------------------------------------------------------------------------------
def is_valid_project(fips_dir, name) :
    """test if a named project directory exists in the fips workspace and
    check whether a fips bootstrap script and fips.yml file exists
    
    :param fips_dir:    absolute path of fips
    :param name:        project/directory name
    :returns:           True if this is a valid fips project
    """
    proj_dir = util.get_proj_dir(fips_dir, name)
    if os.path.isdir(proj_dir) :
        if not os.path.isfile(proj_dir + '/fips') :
            log.error("no file 'fips' in project dir '{}'\n".format(proj_dir), False)
            return False
        if not os.path.isfile(proj_dir + '/fips.yml') :
            log.error("no file 'fips.yml' in project dir '{}'\n".format(proj_dir), False)
            return False
        return True
    return False

#-------------------------------------------------------------------------------
def init(fips_dir, url) :
    """clone an existing, empty git project and setup as fips project, 
    the project will be cloned into a sister directory of fips named 'name',
    a bootstrap-fips script and fips.yml file will be copied.

    :param fips_dir:    absolute path to fips
    :param url:         the git url to clone from
    :returns:           True if the project was successfully initialized
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_url(url)
    proj_dir = util.get_project_dir(fips_dir, proj_name)
    if not os.path.isdir(proj_dir) :
        if git.clone(url, proj_name, ws_dir) :
            src = fips_dir + '/templates/fips'
            dst = proj_dir + '/fips'
            if not os.path.isfile(dst) :
                shutil.copy(src, dst)
                os.chmod(dst, 0o744)
                log.info("copied '{}' to '{}'".format(src, dst))
            else :
                log.warn("file '{}' already exists".format(dst))
            src = fips_dir + '/templates/fips.yml'
            dst = proj_dir + '/fips.yml'
            if not os.path.isfile(dst) :
                shutil.copy(src, dst)
                log.info("copied '{}' to '{}'".format(src, dst))
            else :
                log.warn("file '{}' already exists".format(dst))
            log.info("project dir initialized, please edit '{}' next".format(dst))
            return True
        else :
            log.error("failed to 'git clone {}' into '{}'".format(url, proj_dir))
            return False
    else :
        log.error("project dir '{}' already exists".format(proj_dir))
        return False

#-------------------------------------------------------------------------------
def get(fips_dir, url) :
    """clone an existing fips project with git

    :param fips_dir:    absolute path to fips
    :param url:         git url to clone from
    :return:            True if project was successfully cloned
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_url(url)
    proj_dir = util.get_project_dir(fips_dir, proj_name)
    if not os.path.isdir(proj_dir) :
        if git.clone(url, proj_name, ws_dir) :
            return True
        else :
            log.error("failed to 'git clone {}' into '{}'".format(url, proj_dir))
            return False
    else :
        log.error("project dir '{}' already exists".format(proj_dir))
        return False

#-------------------------------------------------------------------------------
def gen(fips_dir, proj_dir, build_dir, cfg_name, proj_name) :
    """generate build files with cmake

    :param fips_dir:    absolute path to fips
    :param proj_dir:    absolute path to project
    :param build_dir:   absolute path to build directory
    :param cfg_name:    config name (e.g. osx-make-debug)
    :param proj_name:   project name (or None to use current project path)
    :returns:           True if successful
    """
    log.error("FIXME FIXME FIXME")

