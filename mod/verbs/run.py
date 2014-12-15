"""run built exes

run [target]
run [target] [config]
run [target] [config] [project]
"""

from mod import log, config, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run fips project build targets"""
    cfg_name = settings.get(proj_dir, 'config')
    target_name = settings.get(proj_dir, 'target')
    proj_name = None
    if len(args) > 0 :
        target_name = args[0]
    if len(args) > 1:
        cfg_name = args[1]
    if len(args) > 2:
        proj_name = args[2]
    if target_name :
        project.run(fips_dir, proj_dir, cfg_name, proj_name, target_name)
    else :
        log.error('no target provided')


#-------------------------------------------------------------------------------
def help() :
    """print run help"""
    log.info(log.YELLOW + 
            "fips run\n"
            "fips run [target]\n" 
            "fips run [target] [config]\n"
            "fips run [target] [config] [project]\n" + log.DEF +
            "   run a build target for current or named config and project")

