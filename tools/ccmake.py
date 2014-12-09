'''
    ccmake.py

    Wrap the ccmake command line tool.
'''
import subprocess

#-------------------------------------------------------------------------------
def check() :
    '''
    Check if ccmake is in the path.
    '''
    try:
        out = subprocess.check_output(['ccmake', '--version'])
        print 'ccmake found'
        return True
    except OSError:
        print 'ccmake NOT FOUND'
        return False

#-------------------------------------------------------------------------------
def run(build_dir) :
    '''
    Run ccmake to configure the cmake build.
    '''
    cmdLine = ['ccmake', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0


