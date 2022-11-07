"""wrapper for cmake tool"""
import subprocess, json, os

from mod import log, util
from mod import config

name = 'cmake'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = 'please install cmake 2.8 or newer'

#------------------------------------------------------------------------------
def check_exists(fips_dir, major=2, minor=8) :
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
    cmdLine = 'cmake'
    if cfg['generator'] != 'Default' :
        cmdLine += ' -G "{}"'.format(cfg['generator'])
    if cfg['generator-platform'] :
        cmdLine += ' -A "{}"'.format(cfg['generator-platform'])
    if cfg['generator-toolset'] :
        cmdLine += ' -T "{}"'.format(cfg['generator-toolset'])
    cmdLine += ' -DCMAKE_BUILD_TYPE={}'.format(cfg['build_type'])
    if toolchain_path is not None :
        cmdLine += ' -DCMAKE_TOOLCHAIN_FILE={}'.format(toolchain_path)
    cmdLine += ' -DFIPS_CONFIG={}'.format(cfg['name'])
    if local_build:
        cmdLine += ' -DFIPS_LOCAL_BUILD=ON'
    else:
        cmdLine += ' -DFIPS_LOCAL_BUILD=OFF'
    if cfg['defines'] is not None :
        for key in cfg['defines'] :
            val = cfg['defines'][key]
            if type(val) is bool :
                cmdLine += ' -D{}={}'.format(key, 'ON' if val else 'OFF')
            else :
                cmdLine += ' -D{}="{}"'.format(key, val)
    for key in defines :
        cmdLine += ' -D{}={}'.format(key, defines[key])
    cmdLine += ' -B' + build_dir
    cmdLine += ' -H' + project_dir

    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
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
def write_presets(cfg, fips_dir, proj_dir, build_dir, local_build, toolchain_path, defines) :
    """write a CMakeUserPresets.json file

    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain:       toolchain path or None
    :returns:               True if cmake returned successful
    """

    # either modify existing presets file, or create a fresh one
    cmake_presets_filename = f'{proj_dir}/CMakeUserPresets.json'
    if os.path.exists(cmake_presets_filename):
        with open(cmake_presets_filename, 'r') as f:
            cmake_presets = json.load(f)
    else:
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
                    'configurePreset': 'default'
                }
            ]
        }

    # setup a new preset
    preset = {
        'name': cfg['name'],
        'displayName': cfg['name'],
        'binaryDir': build_dir,
    }
    if cfg['generator'] != 'Default':
        preset['generator'] = cfg['generator']
    if 'cmake-toolchain' in cfg:
        preset['toolchainFile'] = config.get_toolchain(fips_dir, proj_dir, cfg)
    if cfg['generator-platform'] :
        preset['architecture'] = cfg['generator-platform']
    if cfg['generator-toolset'] :
        preset['toolset'] = cfg['toolset']
    preset['cacheVariables'] = {
        'CMAKE_BUILD_TYPE': cfg['build_type'],
        'FIPS_CONFIG': cfg['name'],
        'FIPS_LOCAL_BUILD': 'ON' if local_build else 'OFF',
    }
    if cfg['defines'] is not None:
        for key in cfg['defines']:
            val = cfg['defines'][key]
            if type(val) is bool:
                preset['cacheVariables'][key] = 'ON' if val else 'OFF'
            elif type(val) is int:
                preset['cacheVariables'][key] = str(val)
            else :
                preset['cacheVariables'][key] = val
    for key in defines :
        preset['cacheVariables'][key] = defines[key]

    # either overwrite existing preset, or append
    for i, existing_preset in enumerate(cmake_presets['configurePresets']):
        if existing_preset['name'] == preset['name']:
            cmake_presets['configurePresets'][i] = preset
            break
    else:
        cmake_presets['configurePresets'].append(preset)

    with open(f'{proj_dir}/CMakeUserPresets.json', 'w') as f:
        f.write(json.dumps(cmake_presets, indent=2))
