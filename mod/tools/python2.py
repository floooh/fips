"""wrapper for python2, required by emscripten"""
import subprocess

name = 'python2'
platforms = ['osx', 'linux']
optional = True
not_found = "required for emscripten, on OSX run 'brew install python'"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        subprocess.check_output(['python2', '--version'], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False

