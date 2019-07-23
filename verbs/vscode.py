"""helper verb for VSCode support

vscode clean    -- removes all .vscode directories in all dependencies
"""
from mod import log, util
from mod.tools import vscode

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    if len(args) > 0:
        if args[0] == 'clean':
            vscode.cleanup(fips_dir, proj_dir)
        else:
            log.error("invalid noun '{}' (expected: clean)".format(args[0]))

#-------------------------------------------------------------------------------
def help():
    log.info(log.YELLOW +
             "fips vscode clean\n"
             + log.DEF +
             "    delete .vscode directories (useful before git operations)")
