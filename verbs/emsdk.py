"""
    emscripten SDK installation and maintenance
"""
from mod import log, emsdk

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    if len(args) > 0:
        cmd = args[0]
        if cmd == 'install':
            emsdk_version = None
            if len(args) > 1:
                emsdk_version = args[1]
            emsdk.install(fips_dir, emsdk_version)
        elif cmd == 'list':
            emsdk.list(fips_dir)
        elif cmd == 'activate':
            if len(args) > 1:
                emsdk_version = args[1]
                emsdk.activate(fips_dir, emsdk_version)
            else:
                log.error("emscripten SDK version expected (run './fips emsdk list')")
        elif cmd == 'uninstall':
            emsdk.uninstall(fips_dir)
        elif cmd == 'show-config':
            emsdk.show_config(fips_dir)
        elif cmd == 'show-em-config':
            log.info(emsdk.get_em_config(fips_dir))
        elif cmd == 'show-emscripten-root':
            log.info(emsdk.get_emscripten_root(fips_dir))
        else:
            log.error("unknown subcommand '{}' (run './fips help emsdk')".format(cmd))
    else:
        log.error("expected a subcommand (install, list, activate, update or uninstall)")

#-------------------------------------------------------------------------------
def help():
    log.info(log.YELLOW +
             "fips emsdk install [emsdk-version]\n"
             "fips emsdk list\n"
             "fips emsdk activate emsdk-version\n"
             "fips emsdk uninstall\n"
             "fips emsdk show-config\n"
             "fips emsdk show-em-config\n"
             "fips emsdk show-emscripten-root\n"
             + log.DEF +
             "    install and maintain the emscripten SDK")
