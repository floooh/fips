"""implement the 'clean' verb

clean
clean all
clean [config]
"""

from mod import log, util, settings, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """clean generated files"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    if cfg_name == 'all' :
        cfg_name = '*'
    project.clean(fips_dir, proj_dir, cfg_name)
    
#-------------------------------------------------------------------------------
def help() :
    """print 'clean' help"""
    log.info(log.YELLOW + 
            "fips clean\n" 
            "fips clean all\n"
            "fips clean [config]\n" + log.DEF + 
            "    clean generated build files for config")
    
        
        
    
