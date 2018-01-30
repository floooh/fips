"""wrapper for javac, only check_exists"""
import subprocess

name = 'javac'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "a current Java JDK is required for Android development"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['javac', '-version'], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False



