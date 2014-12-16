"""fips main module"""

VERSION = '0.0.1'

from mod import log
from mod.verbs import diag, list, init, clone, gen, build, set, unset, fetch
from mod.verbs import run as vrun   # prevent collision with run() function
try :
    import yaml 
except ImportError:
    log.error("could not import 'yaml', run 'pip --user install PyYAML' to install")

verbs = {
    'diag': diag,
    'list': list,
    'init': init,
    'clone': clone,
    'gen': gen,
    'build': build,
    'run': vrun,
    'set': set,
    'unset': unset,
    'fetch': fetch
}

#-------------------------------------------------------------------------------
def show_help(args) :
    """show help text"""
    if len(args) > 0 :
        # show help for one verb
        verb = args[0]
        if verb in verbs :
            verbs[verb].help()
        else :
            log.error("unknown verb '{}'".format(verb))
    else :
        # show generic help
        log.info("fips: the high-level, multi-platform build system wrapper\n"
                 "v{}\n"
                 "https://www.github.com/floooh/fips\n".format(VERSION))
        for verb in [list, diag, init, clone, gen, build, vrun, set, unset, fetch] :
            verb.help()
            log.info(' ')

#-------------------------------------------------------------------------------
def run(fips_path, proj_path, args) :
    if len(args) <= 1:
        print("run 'fips help' for more info")
    else :
        verb = args[1]
        verb_args = args[2:]
        if verb == 'help' or verb == '--help' or verb == '-help' :
            show_help(verb_args)
        elif verb == '--version' :
            log.info(VERSION)
        elif verb in verbs :
            verbs[verb].run(fips_path, proj_path, verb_args)
        else :
            log.error("unknown verb '{}'".format(verb))







