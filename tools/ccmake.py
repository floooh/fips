'''
    ccmake.py

    Wrap the ccmake command line tool.
'''
import subprocess

name = 'ccmake'
platforms = ['Linux', 'Darwin']

#-------------------------------------------------------------------------------
def check_exists() :
    '''
    Check if ccmake is in the path.
    '''
    try:
        out = subprocess.check_output(['ccmake', '--version'])
        return True
    except OSError:
        return False

#-------------------------------------------------------------------------------
def run(build_dir) :
    '''
    Run ccmake to configure the cmake build.
    '''
    cmdLine = ['ccmake', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0


