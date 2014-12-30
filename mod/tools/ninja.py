"""wrapper for ninja build tool"""
import subprocess

name = 'ninja'
platforms = ['linux', 'osx']
optional = True
not_found = "required for building '*-ninja-*' configs"

#------------------------------------------------------------------------------
def check_exists() :
    """test if ninja is in the path
    
    :returns: True if ninja is in the path
    """
    try:
        out = subprocess.check_output(['ninja', '--version'])
        return True
    except OSError:
        return False;

#-------------------------------------------------------------------------------
def run_build(target, build_dir, num_jobs=1) :
    """build a target

    :param target:      name of build target, of None
    :param build_dir:   directory of the build.ninja file
    :param num_jobs:    number of parallel jobs (default: 1)
    :returns:           True if build was successful
    """
    cmdLine = ['ninja', '-j', str(num_jobs)]
    if target is not None :
        cmdLine.append(target)
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(build_dir) :
    """run the special 'clean' target

    :param build_dir:   directory of the build.ninja file
    :returns:           True if ninja returned without error
    """
    res = subprocess.call(['ninja', 'clean'], cwd=build_dir)
    return res == 0


