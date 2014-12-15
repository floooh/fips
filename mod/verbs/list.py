"""lists stuff

list all            -- list everything
list build-tools    -- list supported build tools
list build-types    -- list supported build types
list platforms      -- list supported platform names
list generators     -- list supported generator names
list configs        -- list available configs
list registry       -- list content of fips registry
list settings       -- list fips settings of current project
list                -- same as 'list all'
"""

from mod import log, config, registry, project, settings

#-------------------------------------------------------------------------------
def list_build_tools() :
    """list supported build tools"""
    log.colored(log.YELLOW, '=== build-tools:')
    for tool in config.build_tools :
        log.info('{}'.format(tool))

#-------------------------------------------------------------------------------
def list_build_types() :
    """list supported build types"""
    log.colored(log.YELLOW, '=== build-types:')
    for type in config.build_types :
        log.info('{}'.format(type))

#-------------------------------------------------------------------------------
def list_platforms() :
    """list supported platforms"""
    log.colored(log.YELLOW, '=== platforms:')
    for p in config.platforms :
        log.info('{}'.format(p))

#-------------------------------------------------------------------------------
def list_generators() :
    """list supported generatores"""
    log.colored(log.YELLOW, '=== generators:')
    for gen in config.generators :
        log.info('{}'.format(gen))

#-------------------------------------------------------------------------------
def list_configs(fips_dir) :
    """list available configs"""
    log.colored(log.YELLOW, '=== configs:')
    dirs = [ fips_dir ]
    configs = config.list('*', dirs)
    for folder in configs :
        log.info('{}:'.format(folder))
        for cfg in configs[folder] :
            log.info('  {}'.format(cfg))

#-------------------------------------------------------------------------------
def list_registry(fips_dir) :
    """list registry entries"""
    log.colored(log.YELLOW, '=== registry:')
    registry.load(fips_dir)
    for key in registry.registry :
        log.info('{}{}{}: {}'.format(log.BLUE, key, log.DEF, registry.registry[key]))

#-------------------------------------------------------------------------------
def list_settings(proj_dir) :
    """list settings file content"""
    log.colored(log.YELLOW, '=== settings:')
    if project.is_valid_project_dir(proj_dir) :
        cfg_name = settings.get(proj_dir, 'config')
        cfg_default = ' (default value)' if cfg_name == settings.get_default('config') else ''
        tgt_name = settings.get(proj_dir, 'target')
        tgt_default = ' (default value)' if tgt_name == settings.get_default('target') else ''
        log.info('  config: {}{}'.format(cfg_name, cfg_default))
        log.info('  target: {}{}'.format(tgt_name, cfg_default))
    else :
        log.info('  not in a valid project directory')

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """list stuff
    
    :param fips_dir:    absolute path to fips
    :param proj_dir:    absolute path to current project
    :param args:        command line args
    """
    noun = 'all'
    ok = False
    if len(args) > 0 :
        noun = args[0]
    if noun in ['all', 'configs'] :
        list_configs(fips_dir)
        ok = True
    if noun in ['all', 'build-tools'] :
        list_build_tools()
        ok = True
    if noun in ['all', 'build-types'] :
        list_build_types()
        ok = True
    if noun in ['all', 'platforms'] :
        list_platforms()
        ok = True
    if noun in ['all', 'generators'] :
        list_generators()
        ok = True
    if noun in ['all', 'registry'] :
        list_registry(fips_dir)
        ok = True
    if noun in ['all', 'settings'] :
        list_settings(proj_dir)
        ok = True

    if not ok :
        log.error("invalid noun '{}'".format(noun))

#-------------------------------------------------------------------------------
def help() :
    """print help text for list verb"""
    log.info(log.YELLOW +
             "fips list\n"
             "fips list all\n"
             "fips list configs\n"
             "fips list build-tools\n"
             "fips list build-types\n"
             "fips list platforms\n"
             "fips list generators\n"
             "fips list registry\n"
             "fips list settings\n"
             + log.DEF +
             "    list available configs, build-tools, etc...")


