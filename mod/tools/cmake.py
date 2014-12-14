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
def run_gen(generator, build_type, defines, toolchain_path, build_dir, project_dir) :
    """run cmake tool to generate build files
    
    :param generator:       the cmake generator (e.g. "Unix Makefiles", "Ninja", ...)
    :param build_type:      CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param toolchain_path:  path to toolchain file, or None
    :param defines:         additional defines (array of key/value pairs)
    :param build_dir:       path to where the build files are generated
    :param project_dir:     path to where the root CMakeLists.txt file lives
    :returns:               True if cmake returned successful
    """
    cmdLine = ['cmake', '-G', generator, '-DCMAKE_BUILD_TYPE={}'.format(build_type)]
    if toolchain_path is not None :
        cmdLine.append('-DDCMAKE_TOOLCHAIN_FILE={}'.format(toolchain))
    if defines is not None :
        for key in defines :
            cmdLine.append('-D{}={}'.format(key, defines[key]))
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

