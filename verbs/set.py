"""set a default config or target

set config [config-name]
set target [target-name]
"""

from mod import log, util, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'set' verb"""

    # FIXME: thos shouldn't be as hardwired as it is, see help() function
    if len(args) > 0 :
        noun = args[0]
        if noun == 'config' :
            if len(args) > 1 :
                cfg_name = args[1]
                settings.set(proj_dir, 'config', cfg_name)
            else :
                log.error('expected config name')
        elif noun == 'target' :
            if len(args) > 1 :
                target_name = args[1]
                settings.set(proj_dir, 'target', target_name)
            else :
                log.error('expected target name')
        elif noun == 'jobs' :
            if len(args) > 1 :
                num_jobs = args[1]
                if num_jobs.isdigit() :
                    settings.set(proj_dir, 'jobs', int(num_jobs))
                else :
                    log.error("value for setting 'jobs' must be a number")
            else :
                log.error('expected number of build jobs value')
        elif noun == 'ccache' :
            if len(args) > 1 :
                use_ccache = args[1]
                if use_ccache == 'on' :
                    settings.set(proj_dir, 'ccache', True)
                elif use_ccache == 'off' :
                    settings.set(proj_dir, 'ccache', False)
                else :
                    log.error("value for setting 'ccache' must be 'on' or 'off")
        elif noun == 'local':
            if len(args) > 1:
                is_local = args[1]
                if is_local == 'on':
                    settings.set(proj_dir, 'local', True)
                elif is_local == 'off':
                    settings.set(proj_dir, 'local', False)
                else:
                    log.error("value for setting 'local' must be 'on' or 'off'")
        elif noun == 'vscode-launch-configs' :
            if len(args) > 1 and args[1] in ['all', 'minimal', 'skip-build']:
                settings.set(proj_dir, noun, args[1])
            else:
                log.error("expected one of 'all', 'minimal' or 'skip-build'")
        else :
            settings.set(proj_dir, noun, args[1])
    else :
        log.error("expected noun 'config' or 'target'")

#-------------------------------------------------------------------------------
def help() :
    """print 'set' help"""
    help_str = log.YELLOW
    for key in settings.valid_settings:
        help_str += "fips set {} [{}]\n".format(key, settings.value_help[key])
    help_str += log.DEF
    for key in settings.valid_settings:
        help_str += "    {}:\t{}\n".format(key, settings.human_help[key])
    help_str = help_str[:-1]
    log.info(help_str)

