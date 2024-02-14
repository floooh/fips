"""wrapper for cmake tool"""
import subprocess, json

from mod import log, util

name = 'cmake'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = 'please install cmake 3.21 or newer'

#------------------------------------------------------------------------------
def check_exists(fips_dir, major=3, minor=21) :
    """test if cmake is in the path and has the required version

    :returns:   True if cmake found and is the required version
    """
    try:
        out = subprocess.check_output(['cmake', '--version']).decode("utf-8")
        ver = out.split()[2].split('.')
        if int(ver[0]) > major or (int(ver[0]) == major and int(ver[1]) >= minor):
            return True
        else :
            log.info('{}NOTE{}: cmake must be at least version {}.{} (found: {}.{}.{})'.format(
                    log.RED, log.DEF, major, minor, ver[0],ver[1],ver[2]))
            return False
    except (OSError, subprocess.CalledProcessError):
        return False

#------------------------------------------------------------------------------
def run_gen(cfg, fips_dir, project_dir, build_dir, local_build, toolchain_path, defines) :
    """run cmake tool to generate build files

    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain:       toolchain path or None
    :returns:               True if cmake returned successful
    """
    write_presets(cfg, fips_dir, project_dir, build_dir, local_build, toolchain_path, defines)
    res = subprocess.call('cmake --preset default', cwd=project_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_build(fips_dir, target, build_type, build_dir, num_jobs=1, args=None) :
    """run cmake in build mode

    :param target:          build target, can be None (builds all)
    :param build_type:      CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param build_dir:       path to the build directory
    :param num_jobs:        number of parallel jobs (default: 1)
    :param args:            optional string array of cmdline args forwarded to build tool
    :returns:               True if cmake returns successful
    """
    args_str = ''
    if args is not None:
        args_str = ' '.join(args)
    if util.get_host_platform() == 'win':
        # builds faster on windows (MSVC) without --parallel
        cmdLine = 'cmake --build . --config {}'.format(build_type)
    else:
        cmdLine = 'cmake --build . --parallel {} --config {}'.format(num_jobs, build_type)
    if target :
        cmdLine += ' --target {}'.format(target)
    cmdLine += ' -- {}'.format(args_str)
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir) :
    """run cmake in build mode

    :param build_dir:   path to the build directory
    :returns:           True if cmake returns successful
    """
    try :
        res = subprocess.call('cmake --build . --target clean', cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False

#------------------------------------------------------------------------------
def to_cmake_preset_cache_variable_value(val):
    if type(val) is bool:
        return {
            'type': 'BOOL',
            'value': 'ON' if val else 'OFF'
        }
    elif type(val) is int:
        return str(val)
    else :
        return val

#------------------------------------------------------------------------------
def write_presets(cfg, fips_dir, proj_dir, build_dir, local_build, toolchain_path, defines) :
    """write a CMakeUserPresets.json file

    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain_path:  toolchain path or None
    :param defines:         any additional cmake defines
    :returns:               True if cmake returned successful
    """
    cmake_presets = {
        'version': 3,
        'cmakeMinimumRequired': {
            'major': 3,
            'minor': 21,
            'patch': 0
        },
        'configurePresets': [],
        'buildPresets': [
            {
                'name': 'default',
                'configurePreset': 'default',
                'configuration': cfg['build_type'],
            },
            {
                'name': 'debug',
                'configurePreset': 'default',
                'configuration': 'Debug',
            },
            {
                'name': 'release',
                'configurePreset': 'default',
                'configuration': 'Release'
            }
        ]
    }

    config_preset = {
        'name': 'default',
        'displayName': cfg['name'],
        'binaryDir': build_dir,
    }

    if cfg['generator'] is not None:
        config_preset['generator'] = cfg['generator']
    if cfg['generator-platform'] :
        config_preset['architecture'] = cfg['generator-platform']
    if cfg['generator-toolset'] :
        config_preset['toolset'] = cfg['toolset']
    if toolchain_path is not None:
        config_preset['toolchainFile'] = toolchain_path
    config_preset['cacheVariables'] = {
        'CMAKE_BUILD_TYPE': cfg['build_type'],  # ignored on multi-config generators
        'FIPS_CONFIG': cfg['name'],
        'FIPS_LOCAL_BUILD': 'ON' if local_build else 'OFF',
    }
    if cfg['defines'] is not None:
        for key,val in cfg['defines'].items():
            config_preset['cacheVariables'][key] = to_cmake_preset_cache_variable_value(val)
    for key,val in defines.items():
        config_preset['cacheVariables'][key] = to_cmake_preset_cache_variable_value(val)

    cmake_presets['configurePresets'].append(config_preset)

    with open('{}/CMakeUserPresets.json'.format(proj_dir), 'w') as f:
        f.write(json.dumps(cmake_presets, indent=2))
