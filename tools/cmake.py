'''
    cmake.py

    Wrap the cmake command line tool.
'''
import subprocess

#------------------------------------------------------------------------------
def check() :
    '''
    Check if cmake is in the path and has the right version.
    '''
    try:
        out = subprocess.check_output(['cmake', '--version'])
        ver = out.split()[2].split('.')
        if int(ver[0]) > 2 or int(ver[0]) == 2 and int(ver[2]) >= 8:
            print 'cmake found'
            return True
        else :
            print 'cmake must be at least version 2.8 (found: {}.{}.{})'.format(ver[0],ver[1],ver[2])
            return False
    except OSError:
        print 'cmake NOT FOUND' 
        return False

#------------------------------------------------------------------------------
def run_gen(generator, build_type, defines, toolchain_path, build_dir, project_dir) :
    '''
    Run the cmake tool to generate build files:
    
    generator       - the cmake generator (e.g. "Unix Makefiles", "Ninja", ...)
    build_type      - CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    toolchain_path  - path to toolchain file (can be None)
    defines         - additional defines (key/value pairs)
    build_dir       - path to where the build files are generators
    project_dir     - path to where the root CMakeLists.txt file lives
    '''
    
    cmdLine = ['cmake']
    cmdLine.append('-G')
    cmdLine.append(generator)
    cmdLine.append('-DCMAKE_BUILD_TYPE={}'.format(build_type))
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
    '''
    Run the cmake tool in build mode.

    build_type      - CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    build_dir       - path to the build directory
    '''
    cmdLine = ['cmake', '--build', '.', '--config', build_type]
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0

