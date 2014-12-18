"""git-clone a project or dependencies

clone [git-url]
"""

from mod import log, util, project, registry, dep

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the get verb"""
    if len(args) > 0 :
        name = args[0]
        
        # check project registry to resolve git url
        if registry.exists(fips_dir, name) :
            url = registry.lookup_url(fips_dir, name)
            log.info("registry lookup: {} => {}".format(name, url))
        else :
            url = name
            log.info("'{}' not in fips registry, trying as git url".format(url))
        project.clone(fips_dir, url)
    else :
        log.error("expected one arg [git-url]")

#-------------------------------------------------------------------------------
def help() :
    """print help text for 'clone' verb"""
    log.info(log.YELLOW + "fips clone [project]\n" + log.DEF +
             "    fetch a project directory from a git repo, project is either\n"
             "    a direct git-url, or a project name in the fips registry")
             

