"""initialize a new fips project

init [project]
"""

from mod import log, project, registry

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the init verb"""
    if len(args) > 0 :
        proj_name = args[0]
        project.init(fips_dir, proj_name)
    else :
        log.error("expected one arg [project]")

#-------------------------------------------------------------------------------
def help() :
    """print help text for init verb"""
    log.info(log.YELLOW +
             "fips init [project]\n"
             + log.DEF +
             "    initialize a project directory as fips project")

    

