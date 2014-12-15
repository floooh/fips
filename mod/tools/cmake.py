"""wrapper for cmake tool"""
import subprocess

from mod import log

name = 'cmake'
platforms = ['linux', 'osx', 'win']

# required version
major = 2
minor = 8

#------------------------------------------------------------------------------
def check_exists() :
    """test if cmake is in the path and has the required version
    
    :returns:   True if cmake found and is the required version
    """
    try:
        out = subprocess.check_output(['cmake', '--version'], universal_newlines=True)
        ver = out.split()[2].split('.')
        if int(ver[0]) > major or int(ver[0]) == major and int(ver[2]) >= minor:
            return True
        else :
            log.info('{}NOTE{}: cmake must be at least version {}.{} (found: {}.{}.{})'.format(
                    log.RED, log.DEF, major, minor, ver[0],ver[1],ver[2]))
            return False
    except OSError:
        return False

#------------------------------------------------------------------------------
def run_gen(cfg, project_dir, build_dir, toolchain_path) :
    """run cmake tool to generate build files
    
    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain:       toolchain path or None
    :returns:               True if cmake returned successful
    """
    cmdLine = ['cmake', '-G', cfg['generator'], '-DCMAKE_BUILD_TYPE={}'.format(cfg['build_type'])]
    if toolchain_path is not None :
        cmdLine.append('-DDCMAKE_TOOLCHAIN_FILE={}'.format(toolchain_path))
    cmdLine.append('-DFIPS_CONFIG={}'.format(cfg['name']))
    if cfg['defines'] is not None :
        for key in cfg['defines'] :
            cmdLine.append('-D{}={}'.format(key, cfg['defines'][key]))
    cmdLine.append(project_dir)
    
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0

#------------------------------------------------------------------------------
def run_build(build_type, build_dir) :
    """run cmake in build mode

    :param build_type:      CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param build_dir:       path to the build directory
    :returns:               True if cmake returns successful
    """
    cmdLine = ['cmake', '--build', '.', '--config', build_type]
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0

#------------------------------------------------------------------------------
def run_clean(build_dir) :
    """run cmake in build mode

    :param build_dir:   path to the build directory
    :returns:           True if cmake returns successful    
    """
    cmdLine = ['cmake', '--build', '.', '--target', 'clean']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0

