"""
    wrapper for node's http-server module, this is preferred over
    python's SimpleHTTPServer module because it supports
    HTTP range requests
"""
import subprocess

name = 'http-server'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "required for running emscripten targets (npm install http-server -g)"

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try:
        out = subprocess.check_output(['http-server', '-h'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False
