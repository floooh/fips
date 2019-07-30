"""run diagnosis

diag all        -- run all diagnosis functions
diag tools      -- check if required tools can be found
diag configs    -- check all configs
diag imports    -- check all imports
diag            -- same as 'diag all'
"""

from mod.tools import git, cmake, ccmake, cmake_gui, python2, vscode, clion
from mod.tools import make, ninja, xcodebuild, xcrun, java, javac, node, ccache
from mod.tools import httpserver
from mod import config, util, log, dep

#-------------------------------------------------------------------------------
def check_fips(fips_dir) :
    """check whether fips is uptodate"""
    log.colored(log.YELLOW, '=== fips:')
    if git.check_branch_out_of_sync(fips_dir, 'master') :
        log.warn("'fips' is not update, please run 'fips update fips'!")
    else :
        log.colored(log.GREEN, '  uptodate')

#-------------------------------------------------------------------------------
def check_tools(fips_dir) :
    """check whether required command line tools can be found"""
    log.colored(log.YELLOW, '=== tools:')
    tools = [ git, cmake, ccmake, cmake_gui, make, ninja, xcodebuild, xcrun, javac, java, node, python2, ccache, vscode, clion, httpserver ]
    platform = util.get_host_platform()
    for tool in tools:
        if platform in tool.platforms :
            if tool.check_exists(fips_dir) :
                log.ok(tool.name, 'found')
            else :
                if tool.optional :
                    log.optional(tool.name, 'OPTIONAL, NOT FOUND ({})'.format(tool.not_found))
                else :
                    log.failed(tool.name, 'NOT FOUND ({})'.format(tool.not_found))

#-------------------------------------------------------------------------------
def check_configs(fips_dir, proj_dir) :
    """find configs and check if they are valid"""
    log.colored(log.YELLOW, '=== configs:')
    dirs = [ fips_dir ]
    configs = config.load(fips_dir, proj_dir, '*')
    for cfg in configs :
        log.colored(log.BLUE, cfg['name'])
        valid, errors = config.check_config_valid(fips_dir, proj_dir, cfg)
        if valid :
            log.colored(log.GREEN, '  ok')
        else :
            for error in errors :
                log.info('  {}'.format(error))

#-------------------------------------------------------------------------------
def check_imports(fips_dir, proj_dir) :
    """recursively check imports"""
    log.colored(log.YELLOW, '=== imports:')
    if util.is_valid_project_dir(proj_dir) :
        dep.check_imports(fips_dir, proj_dir)
    else :
        log.warn('currently not in a project directory')

#-------------------------------------------------------------------------------
def check_local_changes(fips_dir, proj_dir) :
    """check if any imports have local, uncommitted changes"""
    log.colored(log.YELLOW, '=== local changes:')
    if util.is_valid_project_dir(proj_dir):
        dep.check_local_changes(fips_dir, proj_dir)
    else:
        log.warn('currently not in a project directory')

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run diagnostics

    :param fips_dir:    absolute path to fips directory
    :param proj_dir:    absolute path to current project
    :args:              command line args
    """
    noun = 'all'
    ok = False
    if len(args) > 0 :
        noun = args[0]
    if noun in ['all', 'configs'] :
        check_configs(fips_dir, proj_dir)
        ok = True
    if noun in ['all', 'imports'] :
        check_imports(fips_dir, proj_dir)
        ok = True
    if noun in ['all', 'local-changes'] :
        check_local_changes(fips_dir, proj_dir)
        ok = True
    if noun in ['all', 'tools'] :
        check_tools(fips_dir)
        ok = True
    if noun in ['all', 'fips'] :
        check_fips(fips_dir)
        ok = True
    if not ok :
        log.error("invalid noun '{}'".format(noun))

#-------------------------------------------------------------------------------
def help() :
    """print help for diag verb"""
    log.info(log.YELLOW +
             "fips diag\n"
             "fips diag all\n"
             "fips diag fips\n"
             "fips diag tools\n"
             "fips diag configs\n"
             "fips diag imports\n"
             "fips diag local-changes\n"
             + log.DEF +
             "    run diagnostics and check for errors")

