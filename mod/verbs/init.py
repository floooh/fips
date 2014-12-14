"""initialize a new fips project

init [name] [giturl]
"""

from mod.tools import git
from mod import log, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """initialize an existing, empty git project as fips project, the
    new project will be cloned into a sister directory of fips named 'name'

    :param fips_dir:    absolute path to fips 
    :param name:        project name
    :param url:         the git url
    :returns:           True if successful
    """
    if len(args) >= 2 :
        name = args[0]
        url  = args[1]
        project.init(fips_dir, name, url)
    else :
        log.error("one ore more args missing (expected: 'fips init [name] [url]')")

#-------------------------------------------------------------------------------
def help() :
    """print help text for init verb"""
    log.info(log.YELLOW +
             "fips init [name] [url]\n"
             + log.DEF +
             "    clone empty github repo and initialize as fips project")

    

