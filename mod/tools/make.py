"""
wrapper for make tool 
"""
import subprocess

name = 'make'
platforms = ['linux', 'osx', 'win']
optional = True
not_found = "required for building '*-make-*' configs"

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if make tool is in the path
    
    :returns: True if make tool is in path
    """
    try:
        out = subprocess.check_output(['make', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def run_build(fips_dir, target, build_dir, num_jobs=1) :
    """make a build target

    :param target:      name of build target, or None
    :param build_dir:   directory where Makefile is located
    :param num_jobs:    number of jobs, default is 1
    :returns:           True if build was successful
    """
    cmdLine = 'make -j{}'.format(num_jobs)
    if target is not None :
        cmdLine += ' ' + target;
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir) :
    """run the special 'clean' target

    :param build_dir:   directory where Makefile is located
    :returns:           True if make returned with success
    """
    try :
        res = subprocess.call('make clean', cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False


    
    
