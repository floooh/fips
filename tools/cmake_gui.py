"""wrap the ccmake-gui tools (Windows only)"""
import subprocess

name = 'cmake-gui'
platforms = ['Windows']

#-------------------------------------------------------------------------------
def check_exists() :
    """test if cmake-gui is in the path"""
    try:
        out = subprocess.check_output(['cmake-gui', '--version'])
        return True
    except OSError:
        return False;
        
#-------------------------------------------------------------------------------
def run(build_dir) :
    """run the cmake-gui tool

    build_dir -- directory where cmake-generated build files are located
    """
    cmdLine = ['ccmake-gui', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0
    
