'''
    xcodebuild.py

    Wrap the xcodebuild tool.
'''
import subprocess

#------------------------------------------------------------------------------
def check_exists() :
    try :
        subprocess.check_output(['xcodebuild', '-version'])
        print 'xcodebuild: found'
        return True
    except OSError:
        print 'xcodebuild NOT FOUND'
        return False

#------------------------------------------------------------------------------
def run_build(target, build_type, build_dir, num_jobs=1) :
    cmdLine = ['xcodebuild', '-jobs', str(num_jobs), '-configuration', build_type]
    if target is not None :
        cmdLine.extend(['-target', target])
    res = subprocess.call(cmdLine, cwd=build_dir)
    return res == 0

#------------------------------------------------------------------------------
def run_clean(build_dir) :
    res = subprocess.call(['xcodebuild', 'clean'], cwd=build_dir)
    return res == 0

    
