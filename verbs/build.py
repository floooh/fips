"""build fips project

build
build [config]
"""

from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """build fips project"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    build_tool_args = None
    if '--' in args:
        idx = args.index('--')
        build_tool_args = args[(idx + 1):]
        args = args[:idx]
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    project.build(fips_dir, proj_dir, cfg_name, None, build_tool_args)

#-------------------------------------------------------------------------------
def help() :
    """print build help"""
    log.info(log.YELLOW + 
            "fips build [-- build tool args]\n" 
            "fips build [config] [-- build tool args]\n" + log.DEF + 
            "    perform a build for current or named config\n" +
            "    any args following a -- will be forwarded to the invoked build tool")
    
