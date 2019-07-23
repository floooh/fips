"""helper verb for CLion support

clion clean     -- removes all .idea directories in all dependencies
"""
from mod import log, util
from mod.tools import clion

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    if len(args) > 0:
        if args[0] == 'clean':
            clion.cleanup(fips_dir, proj_dir)
        else:
            log.error("invalid noun '{}' (expected: clean)".format(args[0]))

#-------------------------------------------------------------------------------
def help():
    log.info(log.YELLOW +
             "fips clion clean\n"
             + log.DEF +
             "    delete the .idea directory (useful before git\n" +
             "    operations, or when switching build configs)")
