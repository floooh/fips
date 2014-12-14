"""lists stuff

list all            -- list everything
list build-tools    -- list supported build tools
list build-types    -- list supported build types
list platforms      -- list supported platform names
list generators     -- list supported generator names
list configs        -- list available configs
list                -- same as 'list all'
"""

from mod import config,log

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
    dirs = [ fips_dir + '/configs' ]
    configs = config.list('*', dirs)
    for folder in configs :
        log.info('{}:'.format(folder))
        for cfg in configs[folder] :
            log.info('  {}'.format(cfg))

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """list stuff
    
    :param fips_dir:    absolute path to fips
    :param proj_dir:    absolute path to current project
    :param args:        command line args
    """
    which = 'all'
    if len(args) > 0 :
        which = args[0]
    if which == 'all' or which == 'build-tools' :
        list_build_tools()
    if which == 'all' or which == 'build-types' :
        list_build_types()
    if which == 'all' or which == 'platforms' :
        list_platforms()
    if which == 'all' or which == 'generators' :
        list_generators()
    if which == 'all' or which == 'configs' :
        list_configs(fips_dir)

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
             + log.DEF +
             "    list available configs, build-tools, build-types, platforms and generators")


