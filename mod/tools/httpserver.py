"""
    wrapper for node's http-server module, this is preferred over
    python's SimpleHTTPServer module because it supports
    HTTP range requests
"""
import subprocess
import platform

from mod import log,util

name = 'http-server'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "required for running emscripten targets (npm install http-server -g)"

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try:
        if platform.system() == 'Windows':
            subprocess.check_output(['http-server', '-h'], shell=True)
        else:
            subprocess.check_output(['http-server', '-h'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, target_name, target_cwd):
    if not check_exists(fips_dir):
        log.error("http-server tool not found (npm install http-server -g)")
        return

    html_name = target_name + '.html'
    if util.get_host_platform() == 'osx' :
        try :
            subprocess.call(
                'open http://localhost:8080/{} ; http-server -c-1 -g'.format(html_name),
                cwd = target_cwd, shell=True)
        except KeyboardInterrupt :
            return
    elif util.get_host_platform() == 'win' :
        try :
            cmd = 'cmd /c start http://localhost:8080/{} && http-server -c-1 -g'.format(html_name)
            subprocess.call(cmd, cwd = target_cwd, shell=True)
        except KeyboardInterrupt :
            return
    elif util.get_host_platform() == 'linux' :
        try :
            subprocess.call(
                'xdg-open http://localhost:8080/{}; http-server -c-1 -g'.format(html_name),
                cwd = target_cwd, shell=True)
        except KeyboardInterrupt :
            return
    else :
        log.error("don't know how to start HTML app on this platform")
