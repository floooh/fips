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
def init(fips_dir, name, url) :
    """clone an exising, empty git project and setup as fips project, 
    the project will be cloned into a sister directory of fips named 'name',
    a bootstrap-fips script and fips.yml file will be copied.

    :param fips_dir:    absolute path to fips
    :param name:        project and directory name
    :param url:         the git url to clone from
    :returns:           True if the project was successfully initialized
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_dir = util.get_project_dir(fips_dir, name)
    if not os.path.exists(proj_dir) :
        if git.clone(url, name, ws_dir) :
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
        log.error("project directory '{}' already exists".format(proj_dir))
        return False

