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
def match(build_tool):
    return build_tool == 'make'
