"""project related functions"""

import os
import shutil

from mod import log, util, config
from mod.tools import git, cmake

#-------------------------------------------------------------------------------
def is_valid_project_dir(proj_dir) :
    """test if the provided directory is a valid fips project (has a
    fips.yml and a fips file)

    :param proj_dir:    absolute project directory to check
    :returns:           True if a valid fips project
    """
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
def is_valid_project(fips_dir, name) :
    """test if a named project directory exists in the fips workspace and
    check whether a fips bootstrap script and fips.yml file exists
    
    :param fips_dir:    absolute path of fips
    :param name:        project/directory name
    :returns:           True if this is a valid fips project
    """
    proj_dir = util.get_project_dir(fips_dir, name)
    return is_valid_project_dir(proj_dir)

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
def clone(fips_dir, url) :
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
def gen(fips_dir, proj_dir, cfg_name, proj_name) :
    """generate build files with cmake

    :param fips_dir:    absolute path to fips
    :param proj_dir:    absolute path to project
    :param cfg_name:    config name or pattern (e.g. osx-make-debug)
    :param proj_name:   project name (or None to use current project path)
    :returns:           True if successful
    """

    # if a project name is given, build a project dir from it
    if proj_name :
        proj_dir = util.get_project_dir(fips_dir, proj_name)
    else :
        proj_name = util.get_project_name_from_dir(proj_dir)

    # check if proj_dir is a valid fips project
    if not is_valid_project_dir(proj_dir) :
        log.error("'{}' is not a valid fips project".format(proj_dir))
    
    # load the config(s)
    configs = config.load(cfg_name, [fips_dir])
    num_valid_configs = 0
    for cfg in configs :
        # check if config is valid
        if config.check_config_valid(cfg) :
            log.colored(log.YELLOW, "=== generating: {}".format(cfg['name']))

            # get build-dir and make sure it exists
            build_dir = util.get_build_dir(fips_dir, proj_name, cfg)
            if not os.path.isdir(build_dir) :
                os.makedirs(build_dir)
            toolchain_path = config.get_toolchain_for_platform(fips_dir, cfg['platform'])
            
            # run cmake for this config
            if cmake.run_gen(cfg, proj_dir, build_dir, toolchain_path) :
                num_valid_configs += 1
            else :
                log.error("failed to generate build files for config '{}'".format(cfg['name']), False)
        else :
            log.error("'{}' is not a valid config".format(cfg['name']), False)

    if num_valid_configs != len(configs) :
        log.error('{} out of {} configs failed!'.format(len(configs) - num_valid_configs, len(configs)))
        return False      
    else :
        log.colored(log.GREEN, '{} configs generated'.format(num_valid_configs))
        return True
