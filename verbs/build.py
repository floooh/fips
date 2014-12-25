"""build fips project

build
build [config]
"""

from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """build fips project"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    project.build(fips_dir, proj_dir, cfg_name)

#-------------------------------------------------------------------------------
def help() :
    """print build help"""
    log.info(log.YELLOW + 
            "fips build\n" 
            "fips build [config]\n" + log.DEF + 
            "   perform a build for current or named config")
    
