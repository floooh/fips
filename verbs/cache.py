"""implements the cache verb

Opens the CMakeCache.txt in a text editor for a given config

cache
cache [config-name]
"""

import os, sys, subprocess
from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    
    proj_name = util.get_project_name_from_dir(proj_dir)

    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')

    build_dir = util.get_build_dir(fips_dir, proj_name, cfg_name)

    cache_file = build_dir + '/CMakeCache.txt'
    if not os.path.isfile(cache_file) :
        log.error('generate project first!')

    if sys.platform == "win32" :
        os.startfile(cache_file)
    else :
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, cache_file])

#-------------------------------------------------------------------------------
def help() :
    """print cache help"""
    log.info(log.YELLOW + 
            "fips cache\n" 
            "fips cache [config]\n" + log.DEF + 
            "   open the CMakeCache file with your default text editor")
    

