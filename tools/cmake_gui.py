'''
    ccmake_gui.py

    Wrap the ccmake-gui tool.
'''
import subprocess

name = 'cmake-gui'
platforms = ['Windows']

#-------------------------------------------------------------------------------
def check_exists() :
    try:
        out = subprocess.check_output(['cmake-gui', '--version'])
        return True
    except OSError:
        return False;
        
#-------------------------------------------------------------------------------
def run(build_dir) :
    cmdLine = ['ccmake-gui', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0
    
