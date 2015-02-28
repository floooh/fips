"""wrapper for ant tool, only check_exists"""
import subprocess

name = 'ant'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = 'required for Android cross-compilation'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['ant', '-version'], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

