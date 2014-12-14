"""initialize a new fips project

init [name] [giturl]
"""

from mod import log, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the init verb"""
    if len(args) >= 1 :
        url  = args[0]
        project.init(fips_dir, url)
    else :
        log.error("one ore more args missing (expected: 'fips init [git-url]')")

#-------------------------------------------------------------------------------
def help() :
    """print help text for init verb"""
    log.info(log.YELLOW +
             "fips init [url]\n"
             + log.DEF +
             "    clone empty github repo and initialize as fips project")

    

