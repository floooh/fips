"""build config functions"""

import os.path
import glob
import yaml
from collections import OrderedDict
from mod import log, util, dep
from mod.tools import cmake, make, ninja, xcodebuild, vscode, clion
from mod import emsdk, android

# non-cross-compiling platforms
native_platforms = [
    'osx',
    'linux',
    'win32',
    'win64'
] 

build_tools = [
    'make',
    'ninja',
    'xcodebuild',
    'cmake',
    'vscode_cmake',
    'vscode_ninja',
    'clion'
]

default_config = {
    'osx':      'osx-xcode-debug',
    'linux':    'linux-make-debug',
    'win':      'win64-vstudio-debug',
}

#-------------------------------------------------------------------------------
def valid_build_tool(name) :
    """test if provided build tool name is valid

    :param name: a build tool nake (make, ninja, ...)
    :returns: True if build tool name is valid
    """
    return name in build_tools

#-------------------------------------------------------------------------------
def get_default_config() :
    """get the default config name for this platform

    :returns:   default config name for this host platform
    """
    return default_config[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_toolchain(fips_dir, proj_dir, cfg) :
    """get the toolchain path location for a config, this first checks
    for a 'cmake-toolchain' attribute, and if this does not exist, builds
    a xxx.toolchain.cmake file from the platform name (only for cross-
    compiling platforms). Toolchain files are searched in the
    following locations:
    - a fips-files/toolchains subdirectory in the project directory
    - a fips-files/toolchains subdirectory in all imported projects
    - finally in the cmake-toolchains subdirectory of the fips directory

    :param fips_dir:    absolute path to fips
    :param plat:        the target platform name
    :returns:           path to toolchain file or None for non-cross-compiling
    """

    # build toolchain file name
    toolchain = None
    if 'cmake-toolchain' in cfg :
        toolchain = cfg['cmake-toolchain']
    else :
        toolchain = '{}.toolchain.cmake'.format(cfg['platform'])
    
    # look for toolchain file in current project directory
    toolchain_dir = util.get_toolchains_dir(proj_dir)
    toolchain_path = None
    if toolchain_dir:
        toolchain_path = toolchain_dir + '/' + toolchain
    if toolchain_path and os.path.isfile(toolchain_path) :
        return toolchain_path
    else :
        # look for toolchain in all imported directories
        _, imported_projs = dep.get_all_imports_exports(fips_dir, proj_dir)
        for imported_proj_name in imported_projs :
            imported_proj_dir = imported_projs[imported_proj_name]['proj_dir']
            toolchain_dir = util.get_toolchains_dir(imported_proj_dir)
            toolchain_path = None
            if toolchain_dir:
                toolchain_path = toolchain_dir + '/' + toolchain
            if toolchain_path and os.path.isfile(toolchain_path):
                return toolchain_path
        else :
            # toolchain is not in current project or imported projects, 
            # try the fips directory
            toolchain_path = '{}/cmake-toolchains/{}'.format(fips_dir, toolchain)
            if os.path.isfile(toolchain_path) :
                return toolchain_path
    # fallthrough: no toolchain file found
    return None

#-------------------------------------------------------------------------------
def exists(pattern, proj_dirs) : 
    """test if at least one matching config exists

    :param pattern:     config name pattern (e.g. 'linux-make-*')
    :param proj_dir:    array of toplevel dirs to search (must have /configs subdir)
    :returns:           True if at least one matching config exists
    """
    for curDir in proj_dirs :
        if len(glob.glob('{}/configs/{}.yml'.format(curDir, pattern))) > 0 :
            return True
    return False

#-------------------------------------------------------------------------------
def get_config_dirs(fips_dir, proj_dir) :
    """return list of config directories, including all imports

    :param fips_dir: absolute fips directory
    :param proj_dir: absolute project directory
    :returns:        list of all directories with config files
    """
    dirs = []
    if fips_dir != proj_dir :
        success, result = dep.get_all_imports_exports(fips_dir, proj_dir)
        if success :
            for dep_proj_name in result :
                dep_proj_dir = result[dep_proj_name]['proj_dir']
                dep_configs_dir = util.get_configs_dir(dep_proj_dir)
                if dep_configs_dir:
                    dirs.append(dep_configs_dir)
        else :
            log.warn("missing import directories, please run 'fips fetch'")
    dirs.append(fips_dir + '/configs')
    return dirs

#-------------------------------------------------------------------------------
def list(fips_dir, proj_dir, pattern) :
    """return { dir : [cfgname, ...] } in fips_dir/configs and
    proj_dir/fips-files/configs

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param pattern:     global pattern for config-name(s)
    :returns:           a map of matching configs per dir
    """
    dirs = get_config_dirs(fips_dir, proj_dir)
    res = OrderedDict()
    for curDir in dirs :
        res[curDir] = []
        paths = glob.glob('{}/*.yml'.format(curDir))
        for path in paths :
            fname = os.path.split(path)[1]
            fname = os.path.splitext(fname)[0]
            res[curDir].append(fname)
        res[curDir].sort()
    return res

#-------------------------------------------------------------------------------
def load(fips_dir, proj_dir, pattern) :
    """load one or more matching configs from fips and current project dir

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param pattern:     config name pattern (e.g. 'linux-make-*')
    :returns:   an array of loaded config objects
    """
    dirs = get_config_dirs(fips_dir, proj_dir)
    configs = []
    for curDir in dirs :
        paths = glob.glob('{}/{}.yml'.format(curDir, pattern))
        for path in paths :
            try :
                with open(path, 'r') as f :
                    cfg = yaml.load(f)
                folder, fname = os.path.split(path)

                # patch path, folder, and name
                cfg['path'] = path
                cfg['folder'] = folder
                cfg['name'] = os.path.splitext(fname)[0]
                if 'generator' not in cfg :
                    cfg['generator'] = 'Default'
                if 'generator-platform' not in cfg :
                    cfg['generator-platform'] = None
                if 'generator-toolset' not in cfg :
                    cfg['generator-toolset'] = None
                if 'defines' not in cfg :
                    cfg['defines'] = None

                # don't append multiple configs with the same name
                for c in configs:
                    if c['name'] == cfg['name']:
                        break
                else:
                    configs.append(cfg)
            except yaml.error.YAMLError as e:
                log.error('YML parse error: {}', e.message)
    return configs

#-------------------------------------------------------------------------------
def missing_build_tools(fips_dir, tool_name) :
    """check if a build tool is installed"""
    missing = []
    if tool_name == 'cmake' :
        if not cmake.check_exists(fips_dir):
            missing.append(cmake.name)
    elif tool_name == 'make' :
        if not make.check_exists(fips_dir):
            missing.append(make.name)
    elif tool_name == 'ninja' :
        if not ninja.check_exists(fips_dir):
            missing.append(ninja.name)
    elif tool_name == 'xcodebuild' :
        if not xcodebuild.check_exists(fips_dir):
            missing.append(xcodebuild.name)
    elif tool_name == 'vscode_cmake' :
        if not vscode.check_exists(fips_dir):
            missing.append(vscode.name)
        if not cmake.check_exists(fips_dir):
            missing.append(cmake.name)
    elif tool_name == 'vscode_ninja' :
        if not vscode.check_exists(fips_dir):
            missing.append(vscode.name)
        if not ninja.check_exists(fips_dir):
            missing.append(ninja.name)
    elif tool_name == 'clion' :
        if not clion.check_exists(fips_dir):
            missing.append(clion.name)
    return missing

#-------------------------------------------------------------------------------
def check_sdk(fips_dir, platform_name) :
    """check whether an external crossplatform-SDK is installed"""
    if platform_name == 'emscripten' :
        return emsdk.check_exists(fips_dir)
    elif platform_name == 'android' :
        return android.check_exists(fips_dir)
    else :
        return True

#-------------------------------------------------------------------------------
def check_config_valid(fips_dir, proj_dir, cfg, print_errors=False) :
    """check if provided config is valid, and print errors if not

    :param cfg:     a loaded config object
    :returns:       (True, [ messages ]) tuple with result and error messages
    """
    messages = []
    valid = True

    # check whether all required fields are present
    # (NOTE: name and folder should always be present since they are appended
    # during loading)
    required_fields = ['name', 'folder', 'platform', 'generator', 'build_tool', 'build_type']
    for field in required_fields :
        if field not in cfg :
            messages.append("missing field '{}' in '{}'".format(field, cfg['path']))
            valid = False
    
    # check if the target platform SDK is installed
    if not check_sdk(fips_dir, cfg['platform']) :
        messages.append("platform sdk for '{}' not installed (see './fips help setup')".format(cfg['platform']))
        valid = False

    # check if build tool is valid
    if not valid_build_tool(cfg['build_tool']) :
        messages.append("invalid build_tool name '{}' in '{}'".format(cfg['build_tool'], cfg['path']))
        valid = False

    # check if the build tool can be found
    missing_tools = missing_build_tools(fips_dir, cfg['build_tool'])
    if missing_tools:
        messages.append("build tool(s) {} not found".format(','.join(missing_tools)))
        valid = False

    # check if the toolchain file can be found (if this is a crosscompiling toolchain)
    if cfg['platform'] not in native_platforms :
        toolchain_path = get_toolchain(fips_dir, proj_dir, cfg)
        if not toolchain_path :
            messages.append("toolchain file not found for config '{}'!".format(cfg['name']))
            valid = False

    if print_errors :
        for msg in messages :
            log.error(msg, False)

    return (valid, messages)

