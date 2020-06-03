"""wrapper for xcodebuild command line tool (OSX only)"""
import subprocess

name = 'xcodebuild'
platforms = ['osx']
optional = False
not_found = 'please install Xcode and Xcode cmd line tools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if xcodebuild is in the path
    
    :returns:   True if xcodebuild is in the path
    """
    try :
        subprocess.check_output(['xcodebuild', '-version'])
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False

#------------------------------------------------------------------------------
def match(build_tool):
    return build_tool == 'xcodebuild'

#------------------------------------------------------------------------------
def run_build(fips_dir, target, build_type, build_dir, num_jobs=1, args=None) :
    """build a target

    :param target:      name of build target, or None
    :param build_type:  CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param build_dir:   directory where xcode project file is located
    :param num_jobs:    number of parallel jobs (default: 1)
    :param args:        optional string array of additional cmdline args
    :returns:           True if xcodebuild returns successful
    """
    if not target :
        target = "ALL_BUILD"
    args_str = ''
    if args is not None:
        args_str = ' '.join(args)
    cmdLine = 'xcodebuild -jobs {} -configuration {} -target {} {}'.format(num_jobs, build_type, target, args_str)
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir) :
    """run the special 'clean' target

    :params build_dir:  directory where the xcode project file is located
    :returns:           True if xcodebuild returns successful
    """
    try :
        res = subprocess.call('xcodebuild clean', cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False

    
