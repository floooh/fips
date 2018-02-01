"""set a default config or target

set config [config-name]
set target [target-name]
"""

from mod import log, util, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'set' verb"""
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
        else :
            settings.set(proj_dir, noun, args[1])
    else :
        log.error("expected noun 'config' or 'target'")

#-------------------------------------------------------------------------------
def help() :
    """print 'set' help"""
    log.info(log.YELLOW + 
            "fips set config [config-name]\n"
            "fips set target [target-name]\n" 
            "fips set jobs [num-build-jobs]\n"
            "fips set ccache [on|off]\n"+ log.DEF +
            "    config: set active build config\n"
            "    target: set active run target\n"
            "    jobs:   set number of parallel build jobs\n"
            "    ccache: enable/disable using ccache")
