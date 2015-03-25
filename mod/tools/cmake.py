"""wrapper for cmake tool"""
import subprocess

from mod import log

name = 'cmake'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = 'please install cmake 2.8 or newer'

# required version
major = 2
minor = 8

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if cmake is in the path and has the required version
    
    :returns:   True if cmake found and is the required version
    """
    try:
        out = subprocess.check_output(['cmake', '--version'], universal_newlines=True)
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
def run_gen(cfg, project_dir, build_dir, toolchain_path, defines) :
    """run cmake tool to generate build files
    
    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain:       toolchain path or None
    :returns:               True if cmake returned successful
    """
    cmdLine = 'cmake -G "{}" -DCMAKE_BUILD_TYPE={}'.format(cfg['generator'], cfg['build_type'])
    if toolchain_path is not None :
        cmdLine += ' -DCMAKE_TOOLCHAIN_FILE={}'.format(toolchain_path)
    cmdLine += ' -DFIPS_CONFIG={}'.format(cfg['name'])
    if cfg['defines'] is not None :
        for key in cfg['defines'] :
            cmdLine += ' -D{}={}'.format(key, cfg['defines'][key])
    for key in defines :
        cmdLine += ' -D{}={}'.format(key, defines[key])
    cmdLine += ' -B' + build_dir
    cmdLine += ' -H' + project_dir
    
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_build(fips_dir, target, build_type, build_dir) :
    """run cmake in build mode

    :param target:          build target, can be None (builds all)
    :param build_type:      CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param build_dir:       path to the build directory
    :returns:               True if cmake returns successful
    """
    cmdLine = 'cmake --build . --config {}'.format(build_type)
    if target :
        cmdLine += ' --target {}'.format(target)
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

