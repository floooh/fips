"""implements the config verb

config
config [config-name]
"""

from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """configure fips project"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    project.configure(fips_dir, proj_dir, cfg_name)

#-------------------------------------------------------------------------------
def help() :
    """print config help"""
    log.info(log.YELLOW + 
            "fips config\n" 
            "fips config [config]\n" + log.DEF + 
            "    configure the current or named build config\n"
            "    (runs ccmake or cmake-gui)")
    

