"""wrapper for java, only check_exists"""
import subprocess

name = 'java'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "required for Android, on OSX run 'brew cask install java'"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False



