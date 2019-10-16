"""wrapper for sccache tool, only check_exists"""
import subprocess

name = 'sccache'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "used with './fips set ccache sccache'"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['sccache', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

