'''
    ninja.py

    Wrapper for ninja tool.

    FIXME: also support ninja on Windows by including a precompiled
    exe.
'''
import subprocess

#------------------------------------------------------------------------------
def check_exists() :
    try:
        out = subprocess.check_output(['ninja', '--version'])
        print 'ninja: found'
        return True
    except OSError:
        print 'ninja: NOT FOUND'
        return False;

#-------------------------------------------------------------------------------
def run_build(target, build_dir, num_jobs=1) :
    cmdLine = ['ninja', '-j', str(num_jobs)]
    if target is not None :
        cmdLine.append(target)
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(build_dir) :
    res = subprocess.call(['ninja', 'clean'], cwd=build_dir)
    return res == 0


