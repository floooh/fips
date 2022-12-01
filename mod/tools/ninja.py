"""wrapper for ninja build tool"""
import subprocess
import platform

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
    return build_tool in ['ninja', 'vscode']
