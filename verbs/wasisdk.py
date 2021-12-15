"""
    wasi-sdk installation and maintenance
"""
from mod import log, wasisdk

def run(fips_dir, proj_dir, args):
    if len(args) > 0:
        cmd = args[0]
        if cmd == 'install':
            wasisdk.install(fips_dir)
        elif cmd == 'uninstall':
            wasisdk.uninstall(fips_dir)
        else:
            log.error("unknown subcommand '{}' (run './fips help wasisdk')".format(cmd))
    else:
        log.error("expected a subcommand (install or uninstall)")
        
def help():
    log.info(log.YELLOW +
             "fips wasisdk install\n"
             "fips wasisdk uninstall\n"
             + log.DEF +
             "    install or uninstall the WASI SDK")
