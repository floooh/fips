"""generate project build files

gen
gen [config]
gen [config] [project]
"""

from mod import log,util,project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the gen verb"""
    cfg_name = None
    proj_name = None
    if len(args) > 0 :
        cfg_name = args[0]
        if len(args) > 1 :
            proj_name = args[1]
    if cfg_name == None :
        log.error("FIXME: use active config!")
    project.gen(fips_dir, proj_dir, cfg_name, proj_name)

#-------------------------------------------------------------------------------
def help() :
    """print gen help"""
    log.info(log.YELLOW + 
            "fips gen\n" 
            "fips gen [config]\n"
            "fips gen [config] [project]\n" + log.DEF +
            "    generate build files for current or named config and project")
    
