"""wrapper for ant tool, only check_exists"""
import subprocess

name = 'ant'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = 'required for Android cross-compilation'

#------------------------------------------------------------------------------
def check_exists() :
    try :
        subprocess.check_output(['ant', '-version'])
        return True
    except OSError:
        return False


