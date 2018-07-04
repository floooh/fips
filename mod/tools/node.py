"""wrapper for node.js, only check_exists"""
import subprocess

name = 'node'
platforms = ['linux']
optional = True
not_found = 'node.js required for emscripten cross-compiling'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        out = subprocess.check_output(['node', '--version']).decode("utf-8")
        if not out.startswith('v') :
            log.warn("this doesn't look like a proper node.js 'node'")
            return False 
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False


