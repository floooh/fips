'''
    make.py

    Wrap the make tool
'''
import subprocess

name = 'make'
platforms = ['Linux', 'Darwin']

#-------------------------------------------------------------------------------
def check_exists() :
    try:
        out = subprocess.check_output(["make", "--version"])
        return True
    except OSError:
        return False;

#-------------------------------------------------------------------------------
def run_build(target, build_dir, num_jobs=1) :
    cmdLine = ['make', '-j', str(num_jobs)]
    if target is not None :
        cmdLine.append(target)
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(build_dir) :
    res = subprocess.call(['make', 'clean'], cwd=build_dir)
    return res == 0


    
    
