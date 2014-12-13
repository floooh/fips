"""wrapper for ninja build tool"""
import subprocess

name = 'ninja'
platforms = ['Linux', 'Darwin']

#------------------------------------------------------------------------------
def check_exists() :
    """test if ninja is in the path"""
    try:
        out = subprocess.check_output(['ninja', '--version'])
        return True
    except OSError:
        return False;

#-------------------------------------------------------------------------------
def run_build(target, build_dir, num_jobs=1) :
    """build a target

    target      -- name of build target, of None
    build_dir   -- directory of the build.ninja file
    num_jobs    -- number of parallel jobs (default: 1)
    """
    cmdLine = ['ninja', '-j', str(num_jobs)]
    if target is not None :
        cmdLine.append(target)
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(build_dir) :
    """run the special 'clean' target

    build_dir -- directory of the build.ninja file
    """
    res = subprocess.call(['ninja', 'clean'], cwd=build_dir)
    return res == 0


