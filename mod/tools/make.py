"""
wrapper for make tool 
"""
import subprocess

name = 'make'
platforms = ['linux', 'osx']

#-------------------------------------------------------------------------------
def check_exists() :
    """test if make tool is in the path
    
    :returns: True if make tool is in path
    """
    try:
        out = subprocess.check_output(['make', '--version'])
        return True
    except OSError:
        return False;

#-------------------------------------------------------------------------------
def run_build(target, build_dir, num_jobs=1) :
    """make a build target

    :param target:      name of build target, or None
    :param build_dir:   directory where Makefile is located
    :param num_jobs:    number of jobs, default is 1
    :returns:           True if build was successful
    """
    cmdLine = ['make', '-j', str(num_jobs)]
    if target is not None :
        cmdLine.append(target)
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(build_dir) :
    """run the special 'clean' target

    :param build_dir:   directory where Makefile is located
    :returns:           True if make returned with success
    """
    res = subprocess.call(['make', 'clean'], cwd=build_dir)
    return res == 0


    
    
