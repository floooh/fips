"""project related functions"""

import os
import shutil
import subprocess
import yaml

from mod import log, util, config, dep, template, settings, android, emsdk
from mod.tools import git, cmake, make, ninja, xcodebuild, xcrun, ccmake, cmake_gui, vscode, clion, httpserver

#-------------------------------------------------------------------------------
def init(fips_dir, proj_name) :
    """initialize an existing project directory as a fips directory by
    copying essential files and creating or updating .gitignore

    :param fips_dir:    absolute path to fips
    :param proj_name:   project directory name (dir must exist)
    :returns:           True if the project was successfully initialized
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_dir = util.get_project_dir(fips_dir, proj_name)
    if os.path.isdir(proj_dir) :
        templ_values = {
            'project': proj_name
        }
        for f in ['CMakeLists.txt', 'fips', 'fips.cmd', 'fips.yml'] :
            template.copy_template_file(fips_dir, proj_dir, f, templ_values)
        os.chmod(proj_dir + '/fips', 0o744)
        gitignore_entries = ['.fips-*', '*.pyc', '.vscode/', '.idea/']
        template.write_git_ignore(proj_dir, gitignore_entries)
    else :
        log.error("project dir '{}' does not exist".format(proj_dir))
        return False

#-------------------------------------------------------------------------------
def clone(fips_dir, url) :
    """clone an existing fips project with git, do NOT fetch dependencies

    :param fips_dir:    absolute path to fips
    :param url:         git url to clone from (may contain branch name separated by '#')
    :return:            True if project was successfully cloned
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_url(url)
    proj_dir = util.get_project_dir(fips_dir, proj_name)
    if not os.path.isdir(proj_dir) :
        git_url = util.get_giturl_from_url(url)
        git_branch = util.get_gitbranch_from_url(url)
        if git.clone(git_url, git_branch, git.clone_depth, proj_name, ws_dir) :
            # fetch imports
            dep.fetch_imports(fips_dir, proj_dir)
            return True
        else :
            log.error("failed to 'git clone {}' into '{}'".format(url, proj_dir))
            return False
    else :
        log.error("project dir '{}' already exists".format(proj_dir))
        return False

#-------------------------------------------------------------------------------
def gen_project(fips_dir, proj_dir, cfg, force) :
    """private: generate build files for one config"""

    proj_name = util.get_project_name_from_dir(proj_dir)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    defines = {}
    defines['FIPS_USE_CCACHE'] = 'ON' if settings.get(proj_dir, 'ccache') else 'OFF'
    defines['FIPS_AUTO_IMPORT'] = 'OFF' if dep.get_policy(proj_dir, 'no_auto_import') else 'ON'
    if cfg['generator'] in ['Ninja', 'Unix Makefiles']:
        defines['CMAKE_EXPORT_COMPILE_COMMANDS'] = 'ON'
    if cfg['platform'] == 'ios':
        defines['CMAKE_OSX_SYSROOT'] = xcrun.get_ios_sdk_sysroot()
        ios_team_id = settings.get(proj_dir, 'iosteam')
        if ios_team_id:
            defines['FIPS_IOS_TEAMID'] = ios_team_id
    if cfg['platform'] == 'osx':
        defines['CMAKE_OSX_SYSROOT'] = xcrun.get_macos_sdk_sysroot()
    if cfg['platform'] == 'emscripten':
        defines['EMSCRIPTEN_ROOT'] = emsdk.get_emscripten_root(fips_dir)
    do_it = force
    if not os.path.isdir(build_dir) :
        os.makedirs(build_dir)
    if not os.path.isfile(build_dir + '/CMakeCache.txt'):
        do_it = True
    if do_it :
        # if Ninja build tool and on Windows, need to copy
        # the precompiled ninja.exe to the build dir
        log.colored(log.YELLOW, "=== generating: {}".format(cfg['name']))
        log.info("config file: {}".format(cfg['path']))
        toolchain_path = config.get_toolchain(fips_dir, proj_dir, cfg)
        if toolchain_path :
            log.info("Using Toolchain File: {}".format(toolchain_path))
        cmake_result = cmake.run_gen(cfg, fips_dir, proj_dir, build_dir, toolchain_path, defines)
        if vscode.match(cfg['build_tool']):
            vscode.write_workspace_settings(fips_dir, proj_dir, cfg)
        if clion.match(cfg['build_tool']):
            clion.write_workspace_settings(fips_dir, proj_dir, cfg)
        return cmake_result
    else :
        return True

#-------------------------------------------------------------------------------
def gen(fips_dir, proj_dir, cfg_name) :
    """generate build files with cmake

    :param fips_dir:    absolute path to fips
    :param proj_dir:    absolute path to project
    :param cfg_name:    config name or pattern (e.g. osx-make-debug)
    :returns:           True if successful
    """

    # prepare
    dep.fetch_imports(fips_dir, proj_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)
    dep.gather_and_write_imports(fips_dir, proj_dir, cfg_name)

    # load the config(s)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    num_valid_configs = 0
    if configs :
        for cfg in configs :
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors = True)
            if config_valid :
                if gen_project(fips_dir, proj_dir, cfg, True) :
                    num_valid_configs += 1
                else :
                    log.error("failed to generate build files for config '{}'".format(cfg['name']), False)
            else :
                log.error("'{}' is not a valid config".format(cfg['name']), False)
    else :
        log.error("No configs found for '{}'".format(cfg_name))

    if num_valid_configs != len(configs) :
        log.error('{} out of {} configs failed!'.format(len(configs) - num_valid_configs, len(configs)))
        return False
    else :
        log.colored(log.GREEN, '{} configs generated'.format(num_valid_configs))
        return True

#-------------------------------------------------------------------------------
def configure(fips_dir, proj_dir, cfg_name) :
    """run ccmake or cmake-gui on the provided project and config

    :param fips_dir:    absolute fips path
    :param proj_dir:    absolute project dir
    :cfg_name:          build config name
    """

    dep.fetch_imports(fips_dir, proj_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)
    dep.gather_and_write_imports(fips_dir, proj_dir, cfg_name)

    # load configs, if more then one, only use first one
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        cfg = configs[0]
        log.colored(log.YELLOW, '=== configuring: {}'.format(cfg['name']))

        # generate build files
        if not gen_project(fips_dir, proj_dir, cfg, True) :
            log.error("Failed to generate '{}' of project '{}'".format(cfg['name'], proj_name))

        # run ccmake or cmake-gui
        build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
        if ccmake.check_exists(fips_dir) :
            ccmake.run(build_dir)
        elif cmake_gui.check_exists(fips_dir) :
            cmake_gui.run(build_dir)
        else :
            log.error("Neither 'ccmake' nor 'cmake-gui' found (run 'fips diag')")
    else :
        log.error("No configs found for '{}'".format(cfg_name))

#-------------------------------------------------------------------------------
def make_clean(fips_dir, proj_dir, cfg_name) :
    """perform a 'make clean' on the project

    :param fips_dir:    absolute path of fips
    :param proj_dir:    absolute path of project dir
    :param cfg_name:    config name or pattern
    """

    proj_name = util.get_project_name_from_dir(proj_dir)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    num_valid_configs = 0
    if configs :
        for cfg in configs :
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors=True)
            if config_valid :
                log.colored(log.YELLOW, "=== cleaning: {}".format(cfg['name']))

                build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
                result = False
                if make.match(cfg['build_tool']):
                    result = make.run_clean(fips_dir, build_dir)
                elif ninja.match(cfg['build_tool']):
                    result = ninja.run_clean(fips_dir, build_dir)
                elif xcodebuild.match(cfg['build_tool']):
                    result = xcodebuild.run_clean(fips_dir, build_dir)
                else :
                    result = cmake.run_clean(fips_dir, build_dir)

                if result :
                    num_valid_configs += 1
                else :
                    log.error("Failed to clean config '{}' of project '{}'".format(cfg['name'], proj_name))
            else :
                log.error("Config '{}' not valid in this environment".format(cfg['name']))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

    if num_valid_configs != len(configs) :
        log.error('{} out of {} configs failed!'.format(len(configs) - num_valid_configs, len(configs)))
        return False
    else :
        log.colored(log.GREEN, '{} configs cleaned'.format(num_valid_configs))
        return True

#-------------------------------------------------------------------------------
def build(fips_dir, proj_dir, cfg_name, target=None, build_tool_args=None) :
    """perform a build of config(s) in project

    :param fips_dir:        absolute path of fips
    :param proj_dir:        absolute path of project dir
    :param cfg_name:        config name or pattern
    :param target:          optional target name (build all if None)
    :param build_tool_args: optional string array of cmdline args forwarded to the build tool
    :returns:               True if build was successful
    """

    # prepare
    dep.fetch_imports(fips_dir, proj_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)
    dep.gather_and_write_imports(fips_dir, proj_dir, cfg_name)

    # load the config(s)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    num_valid_configs = 0
    if configs :
        for cfg in configs :
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors=True)
            if config_valid :
                log.colored(log.YELLOW, "=== building: {}".format(cfg['name']))

                if not gen_project(fips_dir, proj_dir, cfg, False) :
                    log.error("Failed to generate '{}' of project '{}'".format(cfg['name'], proj_name))

                # select and run build tool
                build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
                num_jobs = settings.get(proj_dir, 'jobs')
                result = False
                if make.match(cfg['build_tool']):
                    result = make.run_build(fips_dir, target, build_dir, num_jobs, build_tool_args)
                elif ninja.match(cfg['build_tool']):
                    result = ninja.run_build(fips_dir, target, build_dir, num_jobs, build_tool_args)
                elif xcodebuild.match(cfg['build_tool']):
                    result = xcodebuild.run_build(fips_dir, target, cfg['build_type'], build_dir, num_jobs, build_tool_args)
                else :
                    result = cmake.run_build(fips_dir, target, cfg['build_type'], build_dir, num_jobs, build_tool_args)

                if result :
                    num_valid_configs += 1
                else :
                    log.error("Failed to build config '{}' of project '{}'".format(cfg['name'], proj_name))
            else :
                log.error("Config '{}' not valid in this environment".format(cfg['name']))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

    if num_valid_configs != len(configs) :
        log.error('{} out of {} configs failed!'.format(len(configs) - num_valid_configs, len(configs)))
        return False
    else :
        log.colored(log.GREEN, '{} configs built'.format(num_valid_configs))
        return True

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, cfg_name, target_name, target_args, target_cwd) :
    """run a build target executable

    :param fips_dir:    absolute path of fips
    :param proj_dir:    absolute path of project dir
    :param cfg_name:    config name or pattern
    :param target_name: the target name
    :param target_args: command line arguments for build target
    :param target_cwd:  working directory or None
    """

    retcode = 10
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)

    # load the config(s)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        for cfg in configs :
            log.colored(log.YELLOW, "=== run '{}' (config: {}, project: {}):".format(target_name, cfg['name'], proj_name))

            # find deploy dir where executables live
            deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
            if not target_cwd :
                target_cwd = deploy_dir

            cmd_line = None
            if cfg['platform'] == 'emscripten':
                # special case: emscripten app
                httpserver.run(fips_dir, proj_dir, target_name, target_cwd)
                return 0
            elif cfg['platform'] == 'android' :
                try :
                    adb_path = android.get_adb_path(fips_dir)
                    pkg_name = android.target_to_package_name(target_name)
                    # Android: first re-install the apk...
                    cmd = '{} install -r {}.apk'.format(adb_path, target_name)
                    subprocess.call(cmd, shell=True, cwd=deploy_dir)
                    # ...then start the apk
                    cmd = '{} shell am start -n {}/android.app.NativeActivity'.format(adb_path, pkg_name)
                    subprocess.call(cmd, shell=True)
                    # ...then run adb logcat
                    cmd = '{} logcat'.format(adb_path)
                    subprocess.call(cmd, shell=True)
                    return 0
                except KeyboardInterrupt :
                    return 0
            elif os.path.isdir('{}/{}.app'.format(deploy_dir, target_name)) :
                # special case: Mac app
                cmd_line = '{}/{}.app/Contents/MacOS/{}'.format(deploy_dir, target_name, target_name)
            else :
                cmd_line = '{}/{}'.format(deploy_dir, target_name)
            if cmd_line :
                if target_args :
                    cmd_line += ' ' + ' '.join(target_args)
                try:
                    retcode = subprocess.call(args=cmd_line, cwd=target_cwd, shell=True)
                except OSError as e:
                    log.error("Failed to execute '{}' with '{}'".format(target_name, e.strerror))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

    return retcode

#-------------------------------------------------------------------------------
def clean(fips_dir, proj_dir, cfg_name) :
    """clean build files

    :param fips_dir:    absolute path of fips
    :param proj_dir:    absolute project path
    :param cfg_name:    config name (or pattern)
    """
    proj_name = util.get_project_name_from_dir(proj_dir)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        num_cleaned_configs = 0
        for cfg in configs :
            build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
            build_dir_exists = os.path.isdir(build_dir)
            deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
            deploy_dir_exists = os.path.isdir(deploy_dir)

            if build_dir_exists or deploy_dir_exists :
                log.colored(log.YELLOW, "=== clean: {}".format(cfg['name']))
                num_cleaned_configs += 1

            if build_dir_exists :
                shutil.rmtree(build_dir)
                log.info("  deleted '{}'".format(build_dir))

            if deploy_dir_exists :
                shutil.rmtree(deploy_dir)
                log.info("  deleted '{}'".format(deploy_dir))
        if num_cleaned_configs == 0 :
            log.colored(log.YELLOW, "=== clean: nothing to clean for {}".format(cfg_name))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

#-------------------------------------------------------------------------------
def get_target_list(fips_dir, proj_dir, cfg_name) :
    """get project targets config name, only works
    if a cmake run was performed before

    :param fips_dir:        absolute path to fips
    :param proj_dir:        absolute project path
    :param cfg_name:        the config name
    :returns:   (success, targets)
    """
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        return util.get_cfg_target_list(fips_dir, proj_dir, configs[0])
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

