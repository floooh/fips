"""implement 'valgrind' verb (debugs a single target with valgrind)

valgrind
valgrind [target]
valgrind [target] [config]
"""

import subprocess

from mod import log, util, config, project, settings

#-------------------------------------------------------------------------------
def valgrind(fips_dir, proj_dir, cfg_name, target, target_args) :
    """debug a single target with valgrind"""

    # prepare
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)

    # load the config(s)
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        for cfg in configs :
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors = True)
            if config_valid :
                deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
                valgrind_bin = settings.get(proj_dir, 'valgrind')
                if not valgrind_bin :
                    valgrind_bin = 'valgrind'
                log.colored(log.YELLOW, "=== valgrind: {} ({})".format(cfg['name'], valgrind_bin))
                cmd_line = valgrind_bin
                if target_args :
                    cmd_line += ' ' + ' '.join(target_args)
                else :
                    cmd_line += ' ' + '--leak-check=no'
                    cmd_line += ' ' + '--show-reachable=yes'
                    cmd_line += ' ' + '--track-fds=yes'
                    cmd_line += ' ' + '--run-libc-freeres=no'
                    cmd_line += ' ' + "--log-file={}/valgrind-{}.log".format(proj_dir, target)
                cmd_line += ' ' + "./{}".format(target)
                #log.colored(log.GREEN, "cmdline: {}".format(cmd_line))
                subprocess.call(args = cmd_line, cwd = deploy_dir, shell = True)
            else :
                log.error("Config '{}' not valid in this environment".format(cfg['name']))
    else :
        log.error("No valid configs found for '{}'".format(cfg_name))

    return True

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """debug a single target with valgrind"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    tgt_name = None
    cfg_name = None
    tgt_args = []
    if '--' in args :
        idx = args.index('--')
        tgt_args = args[(idx + 1):]
        args = args[:idx]
    if len(args) > 0 :
        tgt_name = args[0]
    if len(args) > 1 :
        cfg_name = args[1]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    if not tgt_name :
        tgt_name = settings.get(proj_dir, 'target')
    if not tgt_name :
        log.error('no target specified')
    valgrind(fips_dir, proj_dir, cfg_name, tgt_name, tgt_args)

#-------------------------------------------------------------------------------
def help() :
    """print 'valgrind' help"""
    log.info(log.YELLOW +
            "fips valgrind\n"
            "fips valgrind [target]\n"
            "fips valgrind [target] [config]\n" + log.DEF +
            "   debug a single target in current or named config")
