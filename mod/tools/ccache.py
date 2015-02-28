"""wrapper for ccache tool, only check_exists"""
import subprocess

name = 'ccache'
platforms = ['osx', 'linux']
optional = True
not_found = "used with './fips set ccache on'"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['ccache', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


