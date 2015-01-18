"""lists stuff

list all            -- list everything
list build-tools    -- list supported build tools
list build-types    -- list supported build types
list platforms      -- list supported platform names
list generators     -- list supported generator names
list configs        -- list available configs
list registry       -- list content of fips registry
list settings       -- list fips settings of current project
list exports        -- list project exports
list imports        -- list project imports
list                -- same as 'list all'
"""

from mod import log, util, config, project, registry, settings, dep

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
def list_configs(fips_dir, proj_dir) :
    """list available configs"""
    log.colored(log.YELLOW, '=== configs:')
    configs = config.list(fips_dir, proj_dir, '*')
    for folder in configs :
        log.colored(log.BLUE, 'from {}:'.format(folder))
        for cfg in configs[folder] :
            log.info('  {}'.format(cfg))

#-------------------------------------------------------------------------------
def list_registry(fips_dir) :
    """list registry entries"""
    log.colored(log.YELLOW, '=== registry:')
    registry.load(fips_dir)
    for key in registry.registry :
        log.info('{}{}{} => {}'.format(log.BLUE, key, log.DEF, registry.registry[key]))

#-------------------------------------------------------------------------------
def list_settings(proj_dir) :
    """list settings file content"""
    log.colored(log.YELLOW, '=== settings:')
    if util.is_valid_project_dir(proj_dir) :
        for key in ['config', 'target', 'jobs'] :
            value = settings.get(proj_dir, key)
            default = ' (default value)' if value == settings.get_default(key) else ''
            log.info('  {}{}:{} {}{}'.format(log.BLUE, key, log.DEF, value, default))
    else :
        log.info('  currently not in a valid project directory')

#-------------------------------------------------------------------------------
def list_targets(fips_dir, proj_dir, args) :
    log.colored(log.YELLOW, "=== targets:")
    if util.is_valid_project_dir(proj_dir) :
        # get config name
        if len(args) == 0 :
            cfg_name = settings.get(proj_dir, 'config')
        else :
            cfg_name = args[0]
        log.info('{}  config:{} {}'.format(log.BLUE, log.DEF, cfg_name))

        # get the target list
        success, targets = project.get_target_list(fips_dir, proj_dir, cfg_name)
        if success :
            # split targets by type
            for type in ['lib', 'module', 'app'] :
                type_targets = [tgt for tgt in targets if targets[tgt] == type]
                log.colored(log.BLUE, '  {}:'.format(type))
                for tgt in type_targets :
                    log.info('    ' + tgt)
        else :
            log.info("  can't fetch project target list, please run 'fips gen' first!")  
    else :
        log.info('  currently not in a valid project directory')

#-------------------------------------------------------------------------------
def list_exports(fips_dir, proj_dir) :
    """list project exports"""
    log.colored(log.YELLOW, '=== exports:')
    if util.is_valid_project_dir(proj_dir) :
        success, result = dep.get_all_imports_exports(fips_dir, proj_dir)
        if not success :
            log.warn("missing import project directories, please un 'fips fetch'")
        for dep_proj_name in result :
            cur_dep = result[dep_proj_name]
            log.colored(log.BLUE, "project '{}' exports:".format(dep_proj_name))

            log.info("  modules:")
            cur_modules = cur_dep['exports']['modules']
            if cur_modules :
                for mod in cur_modules :
                    log.info("    {} => {}".format(mod, cur_modules[mod]))
            else :
                log.info("    none")

            log.info("  header search dirs:")
            cur_hdrs = cur_dep['exports']['header-dirs']
            if cur_hdrs :
                for hdr in cur_hdrs :
                    log.info("    {}".format(hdr))
            else :
                log.info("    none")

            log.info("  lib search dirs:")
            cur_libs = cur_dep['exports']['lib-dirs']
            if cur_libs :
                for lib in cur_libs :
                    log.info("    {}".format(lib))
            else :
                log.info("    none")

            log.info("  defines:")
            cur_defs = cur_dep['exports']['defines']
            if cur_defs :
                for define in cur_defs :
                    log.info("    {} => {}".format(define, cur_defs[define]))
            else :
                log.info("    none")
    else :
        log.info('  currently not in a valid project directory')

#-------------------------------------------------------------------------------
def list_imports(fips_dir, proj_dir) :
    """list project imports"""
    log.colored(log.YELLOW, '=== imports:')
    if util.is_valid_project_dir(proj_dir) :
        success, result = dep.get_all_imports_exports(fips_dir, proj_dir)
        if not success :
            log.warn("missing import project directories, please run 'fips fetch'")
        for dep_proj_name in result :
            # top level project is in result, but has no URL set, filter
            # this from the output
            cur_dep = result[dep_proj_name]
            if not cur_dep['url'] :
                log.colored(log.BLUE, "project '{}' imports:".format(dep_proj_name))
            else :
                log.colored(log.BLUE, "project '{}' at '{}' imports:".format(dep_proj_name, cur_dep['url']))
            if cur_dep['imports'] :
                for imp_proj in cur_dep['imports'] :
                    log.info("  {}".format(imp_proj))
            else :
                log.info("    nothing")
    else :
        log.info('  currently not in a valid project directory')

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
        list_configs(fips_dir, proj_dir)
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
    if noun in ['all', 'exports'] :
        list_exports(fips_dir, proj_dir)
        ok = True
    if noun in ['all', 'imports'] :
        list_imports(fips_dir, proj_dir)
        ok = True
    if noun in ['all', 'targets'] :
        list_targets(fips_dir, proj_dir, args[1:])
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
             "fips list targets [config]\n"
             + log.DEF +
             "    list available configs, build-tools, etc...")


