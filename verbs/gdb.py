"""implement 'gdb' verb (debugs a single target with gdb)

gdb
gdb [target]
gdb [target] [config]
"""

import subprocess

from mod import log, util, config, project, settings

#-------------------------------------------------------------------------------
def gdb(fips_dir, proj_dir, cfg_name, target=None) :
    """debug a single target with gdb"""

    # prepare
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)

    # load the config(s)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        for cfg in configs :
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, cfg, print_errors = True)
            if config_valid :
                deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg)
                log.colored(log.YELLOW, "=== gdb: {}".format(cfg['name']))
                cmdLine = ['gdb', target]
                subprocess.call(args = cmdLine, cwd = deploy_dir)
            else :
                log.error("Config '{}' not valid in this environment".format(cfg['name']))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

    if num_valid_configs != len(configs) :
        log.error('{} out of {} configs failed!'.format(len(configs) - num_valid_configs, len(configs)))
        return False
    else :
        log.colored(log.GREEN, '{} configs built'.format(num_valid_configs))
        return True

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """debug a single target with gdb"""
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
    gdb(fips_dir, proj_dir, cfg_name, tgt_name)

#-------------------------------------------------------------------------------
def help() :
    """print 'gdb' help"""
    log.info(log.YELLOW +
            "fips gdb\n"
            "fips gdb [target]\n"
            "fips gdb [target] [config]\n" + log.DEF +
            "   debug a single target in current or named config")
