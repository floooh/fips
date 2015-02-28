"""
wrapper for ccmake command line tool
"""
import subprocess

name = 'ccmake'
platforms = ['linux', 'osx']
optional = True
not_found = "required for 'fips config' functionality"

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if ccmake is in the path
    
    :returns: True if ccmake is in the path
    """
    try:
        out = subprocess.check_output(['ccmake', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def run(build_dir) :
    """run ccmake to configure cmake project

    :param build_dir:   directory where ccmake should run
    :returns:           True if ccmake returns successful
    """
    res = subprocess.call('ccmake .', cwd=build_dir, shell=True)
    return res == 0


