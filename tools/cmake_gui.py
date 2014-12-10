'''
    ccmake-gui.py

    Wrap the ccmake-gui tool.
'''
import subprocess

#-------------------------------------------------------------------------------
def check_exists() :
    try:
        out = subprocess.check_output(['cmake-gui', '--version'])
        print 'cmake-gui: found'
        return True
    except OSError:
        print 'cmake-gui: NOT FOUND'
        return False;
        
#-------------------------------------------------------------------------------
def run(build_dir) :
    cmdLine = ['ccmake-gui', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0
    
