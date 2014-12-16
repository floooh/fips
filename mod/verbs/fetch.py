"""fetch project imports

fetch
fetch [project]
"""

from mod import log, util, dep

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """fetch external project imports

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :args:              additional args
    """
    if len(args) > 0 :
        proj_name = args[0]
        proj_dir = util.get_project_dir(fips_dir, proj_name)
    dep.fetch_imports(fips_dir, proj_dir)

#-------------------------------------------------------------------------------
def help() :
    """print fetch help"""
    log.info(log.YELLOW + 
            "fips fetch\n" 
            "fips fetch [proj]\n" + log.DEF +
            "    fetch external dependencies for current or named project") 


