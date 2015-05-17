"""build config functions"""

import os.path
import glob
import yaml
from collections import OrderedDict
from mod import log, util, dep
from mod.tools import cmake, make, ninja, xcodebuild
from mod import emscripten, nacl, android

platforms = [
    'osx', 
    'linux', 
    'win32', 
    'win64', 
    'emscripten', 
    'pnacl', 
    'ios',
    'android'
]

# non-cross-compiling platforms
native_platforms = [
    'osx',
    'linux',
    'win32',
    'win64'
] 

# cross-compiling platforms
cross_platforms = [
    'emscripten',
    'pnacl',
    'ios',
    'android'
]

# valid target platforms
target_platforms = {
    'osx':      [ 'osx', 'ios', 'emscripten', 'pnacl', 'android' ],
    'linux':    [ 'linux', 'emscripten', 'pnacl', 'android' ],
    'win':      [ 'win32', 'win64', 'emscripten', 'android' ]
}

# supported cmake generators
generators = [
    'Unix Makefiles',
    'Ninja',
    'Xcode',
    'Visual Studio 12',
    'Visual Studio 12 Win64', 
    'Visual Studio 14',
    'Visual Studio 14 Win64',
    'CodeBlocks - Ninja',
    'CodeBlocks - Unix Makefiles',
    'CodeLite - Ninja',
    'CodeLite - Unix Makefiles',
    'Eclipse CDT4 - Ninja',
    'Eclipse CDT4 - Unix Makefiles',
    'KDevelop3',
    'KDevelop3 - Unix Makefiles',
    'Kate - Ninja',
    'Kate - Unix Makefiles',
    'Sublime Text 2 - Ninja',
    'Sublime Text 2 - Unix Makefiles'
]

build_tools = [
    'make',
    'ninja',
    'xcodebuild',
    'cmake'
]

build_types = [
    'Release',
    'Debug',
    'Profiling'
]

default_config = {
    'osx':      'osx-xcode-debug',
    'linux':    'linux-make-debug',
    'win':      'win64-vs2013-debug',
}

#-------------------------------------------------------------------------------
def valid_platform(name) :
    """test if provided platform name is valid

    :param name: platform name (e.g. osx, linux, emscripten, ...)
    :returns: True if platform name is valid
    """
    return name in platforms

#-------------------------------------------------------------------------------
def valid_generator(name) :
    """test if provided cmake generator name is valid

    :param name: generator name (e.g. 'Unix Makefiles', 'Ninja', ...)
    :returns: True if generator name is valid
    """
    return name in generators

#-------------------------------------------------------------------------------
def valid_build_tool(name) :
    """test if provided build tool name is valid

    :param name: a build tool nake (make, ninja, ...)
    :returns: True if build tool name is valid
    """
    return name in build_tools

#-------------------------------------------------------------------------------
def valid_build_type(name) :
    """test if provided build type name is valid

    :param name: build type (Debug, Release, ...)
    :returns: True if build type is valid
    """
    return name in build_types

#-------------------------------------------------------------------------------
def get_default_config() :
    """get the default config name for this platform

    :returns:   default config name for this host platform
    """
    return default_config[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_toolchain_for_platform(fips_dir, plat) :
    """get the toolchain path location for a target platform, returns None
    for 'native host platform

    :param fips_dir:    absolute path to fips
    :param plat:        the target platform name
    :returns:           path to toolchain file or None for non-cross-compiling
    """
    if plat in native_platforms :
        return None
    else :
        return '{}/cmake-toolchains/{}.toolchain.cmake'.format(fips_dir, plat)

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
    dirs = [ fips_dir + '/configs' ]
    if fips_dir != proj_dir :
        success, result = dep.get_all_imports_exports(fips_dir, proj_dir)
        if success :
            for dep_proj_name in result :
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                dep_configs_dir = dep_proj_dir + '/fips-configs'
                if os.path.isdir(dep_configs_dir) :
                    dirs.append(dep_configs_dir)
        else :
            log.warn("missing import directories, please run 'fips fetch'")
    return dirs

#-------------------------------------------------------------------------------
def list(fips_dir, proj_dir, pattern) :
    """return { dir : [cfgname, ...] } in fips_dir/configs and
    proj_dir/fips-configs

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

                if 'defines' not in cfg :
                    cfg['defines'] = None
                
                configs.append(cfg)
            except yaml.error.YAMLError, e:
                log.error('YML parse error: {}', e.message)
    return configs

#-------------------------------------------------------------------------------
def check_build_tool(fips_dir, tool_name) :
    """check if a build tool is installed"""
    if tool_name == 'cmake' :
        return cmake.check_exists(fips_dir)
    elif tool_name == 'make' :
        return make.check_exists(fips_dir)
    elif tool_name == 'ninja' :
        return ninja.check_exists(fips_dir)
    elif tool_name == 'xcodebuild' :
        return xcodebuild.check_exists(fips_dir)
    else :
        return False;

#-------------------------------------------------------------------------------
def check_sdk(fips_dir, platform_name) :
    """check whether an external crossplatform-SDK is installed"""
    if platform_name == 'emscripten' :
        return emscripten.check_exists(fips_dir)
    elif platform_name == 'pnacl' :
        return nacl.check_exists(fips_dir)
    elif platform_name == 'android' :
        return android.check_exists(fips_dir)
    else :
        return True

#-------------------------------------------------------------------------------
def check_config_valid(fips_dir, cfg, print_errors=False) :
    """check if provided config is valid, and print errors if not

    :param cfg:     a loaded config object
    :returns:       (True, [ errors ]) tuple with result and error messages
    """
    errors = []
    valid = True

    # check whether all required fields are present
    # (NOTE: name and folder should always be present since they are appended
    # during loading)
    required_fields = ['name', 'folder', 'platform', 'generator', 'build_tool', 'build_type']
    for field in required_fields :
        if field not in cfg :
            errors.append("missing field '{}' in '{}'".format(field, cfg['path']))
            valid = False
    
    # check if the platform string is valid
    if not valid_platform(cfg['platform']) :
        errors.append("invalid platform name '{}' in '{}'".format(cfg['platform'], cfg['path']))
        valid = False

    # check if the platform can be built on current host platform
    if cfg['platform'] not in target_platforms[util.get_host_platform()] :
        errors.append("'{}' is not a valid target platform for host '{}'".format(cfg['platform'], util.get_host_platform()))
        valid = False

    # check if the target platform SDK is installed
    if not check_sdk(fips_dir, cfg['platform']) :
        errors.append("platform sdk for '{}' not installed (see './fips help setup')".format(cfg['platform']))
        valid = False

    # check if the generator name is valid
    if not valid_generator(cfg['generator']) :
        errors.append("invalid generator name '{}' in '{}'".format(cfg['generator'], cfg['path']))
        valid = False

    # check if build tool is valid
    if not valid_build_tool(cfg['build_tool']) :
        errors.append("invalid build_tool name '{}' in '{}'".format(cfg['build_tool'], cfg['path']))
        valid = False

    # check if the build tool can be found
    if not check_build_tool(fips_dir, cfg['build_tool']) :
        errors.append("build tool '{}' not found".format(cfg['build_tool']))
        valid = False

    # check if build type is valid (Debug, Release, Profiling)
    if not valid_build_type(cfg['build_type']) :
        errors.append("invalid build_type '{}' in '{}'".format(cfg['build_type'], cfg['path']))
        valid = False

    if print_errors :
        for error in errors :
            log.error(error, False)

    return (valid, errors)

