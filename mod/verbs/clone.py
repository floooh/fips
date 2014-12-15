"""get a project or dependencies

get project [url]
get deps
get deps [project]
"""

from mod import log, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the get verb"""
    if len(args) > 0 :
        noun = args[0]
        if noun == 'project' :
            if len(args) > 1 :
                url = args[1]
                project.get(fips_dir, url)
            else :
                log.error("git-url expected (fips get project [url])")
        elif noun == 'deps' :
            log.error("'fips get deps' NOT YET IMPLEMENTED")
    else :
        log.error("noun 'project' or 'deps' expected")

#-------------------------------------------------------------------------------
def help() :
    """print help text for 'get' verb"""
    log.info(log.YELLOW + "fips get project [git-url]\n" + log.DEF +
             "    fetch a project directory from a git repo\n"
             + log.YELLOW + 
             "fips get deps\n"
             "fips get deps [project-name]\n" + log.DEF +
             "    fetch dependencies for current or named project")
             

