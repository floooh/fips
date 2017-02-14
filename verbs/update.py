"""update dependencies (only if no local changes)

update all      -- update all dependencies
update [proj]   -- update a specific dependency
"""

from mod import log, util, dep

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    if len(args) > 0 :
        proj_name = args[0]
        proj_dir = util.get_project_dir(fips_dir, proj_name)
    dep.update_imports(fips_dir, proj_dir)

#-------------------------------------------------------------------------------
def help() :
    log.info(log.YELLOW + 
            "fips update\n" 
            "fips update [proj]\n" + log.DEF +
            "    update external dependencies for current or named project") 
