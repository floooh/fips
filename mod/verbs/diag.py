"""run diagnosis

diag all        -- run all diagnosis functions
diag tools      -- check if required tools can be found
diag configs    -- check all configs
diag            -- same as 'diag all'
"""

from mod.tools import git,cmake,ccmake,cmake_gui,make,ninja,xcodebuild
from mod import config, log

#-------------------------------------------------------------------------------
def check_tools() :
    """check whether required command line tools can be found"""
    log.colored(log.YELLOW, '=== tools:')
    tools = [ git, cmake, ccmake, cmake_gui, make, ninja, xcodebuild ]
    platform = config.get_host_platform()
    for tool in tools:
        if platform in tool.platforms :
            if tool.check_exists() :
                log.ok(tool.name, 'found')
            else :
                log.failed(tool.name, 'NOT FOUND')

#-------------------------------------------------------------------------------
def check_configs(fips_dir) :
    """find configs and check if they are valid"""
    log.colored(log.YELLOW, '=== configs:')
    dirs = [ fips_dir ]
    configs = config.load('*', dirs)
    for cfg in configs :
        if config.check_config_valid(cfg) :
            log.ok(cfg['name'], 'ok')
        else :
            log.failed(cfg['name'], 'FAILED')

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run diagnostics

    :param fips_dir:    absolute path to fips directory
    :param proj_dir:    absolute path to current project
    :args:              command line args
    """
    which = 'all'
    if len(args) > 0 :
        which = args[0]
    if which == 'all' or which == 'tools' :
        check_tools()
    if which == 'all' or which == 'configs' :
        check_configs(fips_dir)

#-------------------------------------------------------------------------------
def help() :
    """print help for diag verb"""
    log.info(log.YELLOW +
             "fips diag\n"
             "fips diag all\n"
             "fips diag tools\n"
             "fips diag configs\n"
             + log.DEF +
             "    run diagnostics and check for errors")



