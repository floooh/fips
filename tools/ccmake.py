"""
wrapper for ccmake command line tool
"""
import subprocess

name = 'ccmake'
platforms = ['Linux', 'Darwin']

#-------------------------------------------------------------------------------
def check_exists() :
    """test if ccmake is in the path"""
    try:
        out = subprocess.check_output(['ccmake', '--version'])
        return True
    except OSError:
        return False

#-------------------------------------------------------------------------------
def run(build_dir) :
    """run ccmake to configure cmake project

    build_dir -- directory where ccmake should run
    """
    cmdLine = ['ccmake', '.']
    res = subprocess.call(args=cmdLine, cwd=build_dir)
    return res == 0


