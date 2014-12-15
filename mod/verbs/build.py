"""build fips project

build
build [config]
build [config] [project]
"""

from mod import log, config, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """build fips project"""
    cfg_name = None
    proj_name = None
    if len(args) > 0 :
        cfg_name = args[0]
        if len(args) > 1 :
            proj_name = args[1]
    if cfg_name == None :
        log.error("FIXME: use active config")
    project.build(fips_dir, proj_dir, cfg_name, proj_name)

#-------------------------------------------------------------------------------
def help() :
    """print build help"""
    log.info(log.YELLOW + 
            "fips build\n" 
            "fips build [config]\n"
            "fips build [config] [project]\n" + log.DEF +
            "   perform a build for current or named config and project")
    
