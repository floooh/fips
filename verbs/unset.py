"""unset a default setting

unset config
unset target
"""

from mod import log, settings

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'unset' verb"""
    if len(args) > 0 :
        noun = args[0]
        if noun == 'config' :
            settings.unset(proj_dir, 'config')
        elif noun == 'target' :
            settings.unset(proj_dir, 'target')
        else :
            log.error("invalid noun '{}', must be 'config' or 'target'")
    else :
        log.error("expected noun 'config' or 'target'")

#-------------------------------------------------------------------------------
def help() :
    """print 'unset' help"""
    log.info(log.YELLOW + 
            "fips unset config\n"
            "fips unset target\n" + log.DEF +
            "    unset currently active config or make-target")
    
