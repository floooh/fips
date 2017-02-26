"""query project info via cmake-server"""

from mod import log,settings,config,util
from mod.tools import cmake
import json

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    if util.is_valid_project_dir(proj_dir) :
        cfg_name = settings.get(proj_dir, 'config')
        cfg = config.load(fips_dir, proj_dir, cfg_name)[0]
        res = cmake.get_codemodel(fips_dir, proj_dir, cfg)
        if res is not None:
            print(json.dumps(res, indent=2, separators=(',',':')))
    else:
        log.error("must be run from a project directory")

#-------------------------------------------------------------------------------
def help():
    log.info(log.YELLOW + 
            "fips cmake-dump\n" + log.DEF + 
            "   dump cmake codemodel info as JSON")
