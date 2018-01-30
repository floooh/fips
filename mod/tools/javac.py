"""wrapper for javac, only check_exists"""
import subprocess

name = 'javac'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "required for Android development, installed with the Java JDK"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['javac', '-version'], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False



