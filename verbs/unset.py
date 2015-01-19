"""unset a default setting

unset config
unset target
"""

from mod import log, settings

valid_nouns = ['config', 'target', 'jobs', 'ccache']

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'unset' verb"""
    if len(args) > 0 :
        noun = args[0]
        if noun in valid_nouns :
            settings.unset(proj_dir, noun)
        else :
            log.error("invalid noun '{}', must be: {}".format(
                noun, ', '.join(valid_nouns)))
    else :
        log.error("expected noun: {}".format(', '.join(valid_nouns)))

#-------------------------------------------------------------------------------
def help() :
    """print 'unset' help"""
    log.info(log.YELLOW + 
            "fips unset [{}]\n" .format('|'.join(valid_nouns)) + log.DEF +
            "    unset currently active config or make-target")


    
