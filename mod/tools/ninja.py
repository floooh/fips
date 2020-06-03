"""wrapper for ninja build tool"""
import subprocess
import platform
import shutil

name = 'ninja'
platforms = ['linux', 'osx', 'win']
optional = True
not_found = "required for building '*-ninja-*' configs"

#-------------------------------------------------------------------------------
def get_ninja_name() :
    if platform.system() == 'Windows' :
        return 'ninja.exe'
    else :
        return 'ninja'

#-------------------------------------------------------------------------------
def get_ninja_tool(fips_dir) :
    """get the ninja tool exe"""
    return get_ninja_name()

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if ninja is in the path
    
    :returns: True if ninja is in the path
    """
    try:
        out = subprocess.check_output(['{}'.format(get_ninja_tool(fips_dir)), '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def match(build_tool):
    return build_tool in ['ninja', 'vscode_ninja']

#-------------------------------------------------------------------------------
def run_build(fips_dir, target, build_dir, num_jobs=1, args=None) :
    """build a target

    :param target:      name of build target, of None
    :param build_dir:   directory of the build.ninja file
    :param num_jobs:    number of parallel jobs (default: 1)
    :param args:        string array of additional command line args
    :returns:           True if build was successful
    """
    if not target :
        target = 'all'
    args_str = ''
    if args is not None:
        args_str = ' '.join(args)
    cmdLine = "{} -j {} {} {}".format(get_ninja_name(), num_jobs, args_str, target)
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir) :
    """run the special 'clean' target

    :param build_dir:   directory of the build.ninja file
    :returns:           True if ninja returned without error
    """
    try :
        cmdLine = '{} clean'.format(get_ninja_name())
        res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False


