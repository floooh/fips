"""fips main module"""

VERSION = '0.0.1'

from colorama import init
init()

import yaml

from mod import log, verb, util

#-------------------------------------------------------------------------------
def show_help(args) :
    """show help text"""
    if len(args) > 0 :
        # show help for one verb
        verb_name = args[0]
        if verb_name in verb.verbs :
            verb.verbs[verb_name].help()
        else :
            log.error("unknown verb '{}'".format(verb))
    else :
        # show generic help
        log.info("fips: the high-level, multi-platform build system wrapper\n"
                 "v{}\n"
                 "https://www.github.com/floooh/fips\n".format(VERSION))
        for proj_name in verb.proj_verbs :
            if proj_name != 'fips' :
                log.colored(log.BLUE, "=== imported from '{}':".format(proj_name))
            for verb_name in verb.proj_verbs[proj_name] :
                verb.verbs[verb_name].help()
                log.info(' ')

#-------------------------------------------------------------------------------
def run(fips_path, proj_path, args) :
    fips_path = util.fix_path(fips_path)
    proj_path = util.fix_path(proj_path)
    if ' ' in proj_path:
        log.warn("whitespace in project path detected, fips will not work correctly")
    verb.import_verbs(fips_path, proj_path)
    if len(args) <= 1:
        print("run 'fips help' for more info")
    else :
        verb_name = args[1]
        verb_args = args[2:]
        if verb_name in ['help', '--help', '-help'] :
            show_help(verb_args)
        elif verb_name == '--version' :
            log.info(VERSION)
        elif verb_name in verb.verbs :
            verb.verbs[verb_name].run(fips_path, proj_path, verb_args)
        else :
            log.error("unknown verb '{}'".format(verb_name))


