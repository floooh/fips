"""generate project build files

gen
gen [config]
"""

from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the gen verb"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if cfg_name == None :
        cfg_name = settings.get(proj_dir, 'config')
    project.gen(fips_dir, proj_dir, cfg_name)

#-------------------------------------------------------------------------------
def help() :
    """print gen help"""
    log.info(log.YELLOW +
            "fips gen\n"
            "fips gen [config]\n" + log.DEF +
            "    generate build files for current or named config")
