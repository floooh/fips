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
        settings.unset(proj_dir, noun)
    else :
        log.error("expected one of [{}] after 'unset".format('|'.join(settings.valid_settings)))

#-------------------------------------------------------------------------------
def help() :
    """print 'unset' help"""
    log.info(log.YELLOW +
            "fips unset [{}]\n" .format('|'.join(settings.valid_settings)) + log.DEF +
            "    unset currently active config or make-target")
