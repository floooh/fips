"""implement 'make' verb (builds a single target)

make
make [target]
make [target] [config]
"""

from mod import log, util, settings, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """build a single target"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    tgt_name = None
    cfg_name = None
    if len(args) > 0 :
        tgt_name = args[0]
    if len(args) > 1:
        cfg_name = args[1]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    if not tgt_name :
        tgt_name = settings.get(proj_dir, 'target')
    if tgt_name == 'clean' :
        project.make_clean(fips_dir, proj_dir, cfg_name)
    else :
        project.build(fips_dir, proj_dir, cfg_name, tgt_name)

#-------------------------------------------------------------------------------
def help() :
    """print 'make' help"""
    log.info(log.YELLOW + 
            "fips make\n" 
            "fips make [target]\n"
            "fips make [target] [config]\n" + log.DEF +
            "   build a single target in current or named config")
    

