"""build config functions"""

import platform
import os.path
import glob
import yaml
from mod import log

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

# supported cmake generators
generators = [
    'Unix Makefiles',
    'Ninja',
    'Xcode',
    'Visual Studio 12',
    'Visual Studio 12 Win64', 
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

host_platforms = {
    'Darwin':   'osx',
    'Linux':    'linux',
    'Windows':  'win'
}

default_config = {
    'osx':      'osx-xcode-debug',
    'linux':    'linux-make-debug',
    'win':      'win64-vstudio-debug',
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
def get_host_platform() :
    """get the current host platform name (osx, linux or win)

    :returns: platform name (osx, linux, win)
    """
    return host_platforms[platform.system()]

#-------------------------------------------------------------------------------
def get_default_config() :
    """get the default config name for this platform

    :returns:   default config name for this host platform
    """
    return default_config[get_host_platform()]

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
def list(pattern, proj_dirs) :
    """return { dir : [cfgname, ...] } of all configs in given dirs

    :param proj_dirs:   array of toplevel dirs to search (must have /configs subdir)
    :returns:           a map of matching configs per dir
    """
    res = {}
    for curDir in proj_dirs :
        res[curDir] = []
        paths = glob.glob('{}/configs/*.yml'.format(curDir))
        for path in paths :
            fname = os.path.split(path)[1]
            fname = os.path.splitext(fname)[0]
            res[curDir].append(fname)
    return res

#-------------------------------------------------------------------------------
def load(pattern, proj_dirs) :
    """load one or more matching configs

    :param pattern:     config name pattern (e.g. 'linux-make-*')
    :param proj_dirs:   array of toplevel dirs to search (must have /configs subdir)
    :returns:   an array of loaded config objects
    """
    configs = []
    for curDir in proj_dirs :
        paths = glob.glob('{}/configs/{}.yml'.format(curDir, pattern))
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
def check_config_valid(cfg) :
    """check if provided config is valid, and print errors if not

    :param cfg:     a loaded config object
    :returns:       True if the config is valid
    """
    valid = True

    # check whether all required fields are present
    # (NOTE: name and folder should always be present since they are appended
    # during loading)
    required_fields = ['name', 'folder', 'platform', 'generator', 'build_tool', 'build_type']
    for field in required_fields :
        if field not in cfg :
            log.error("missing field '{}' in '{}'".format(field, cfg['path']), False)
            valid = False
    
    # check if the platform string is valid
    if not valid_platform(cfg['platform']) :
        log.error("invalid platform name '{}' in '{}'".format(cfg['platform'], cfg['path']), False)
        valid = False

    # check if the generator name is valid
    if not valid_generator(cfg['generator']) :
        log.error("invalid generator name '{}' in '{}'".format(cfg['generator'], cfg['path']), False)
        valid = False

    # check if build tool is valid
    if not valid_build_tool(cfg['build_tool']) :
        log.error("invalid build_tool name '{}' in '{}'".format(cfg['build_tool'], cfg['path']))
        valid = False

    # check if build type is valid (Debug, Release, Profiling)
    if not valid_build_type(cfg['build_type']) :
        log.error("invalid build_type '{}' in '{}'".format(cfg['build_type'], cfg['path']))
        valid = False

    return valid




