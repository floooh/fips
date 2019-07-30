"""update dependencies (only if no local changes)

update          -- update all dependencies
update [proj]   -- update a specific dependency
update fips     -- update fips itself
"""

from mod import log, util, dep
from mod.tools import git

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    if len(args) > 0 and args[0] == 'fips' :
        if git.has_local_changes(fips_dir) :
            log.warn("  '{}' has local changes, skipping...".format(fips_dir))
        else :
            log.colored(log.BLUE, "  updating '{}'...".format(fips_dir))
            git.update(fips_dir)
    else :
        if len(args) > 0 :
            proj_name = args[0]
            proj_dir = util.get_project_dir(fips_dir, proj_name)
        dep.update_imports(fips_dir, proj_dir)

#-------------------------------------------------------------------------------
def help() :
    log.info(log.YELLOW +
            "fips update\n"
            "fips update [proj|fips]\n" + log.DEF +
            "    update external dependencies for current or named project,\n"
            "    or update fips itself")
