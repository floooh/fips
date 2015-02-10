"""implement the 'open' verb

open
open [config]
"""

import os
import glob
import subprocess

from mod import log, util, settings, config, project

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'open' verb (opens project in IDE)"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    proj_name = util.get_project_name_from_dir(proj_dir)
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
        
    # check the cmake generator of this config
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        # hmm, only look at first match, 'open' doesn't
        # make sense with config-patterns
        cfg = configs[0]

        # find build dir, if it doesn't exist, generate it
        build_dir = util.get_build_dir(fips_dir, proj_name, cfg)
        if not os.path.isdir(build_dir) :
            log.warn("build dir not found, generating...")
            project.gen(fips_dir, proj_dir, cfg['name'])

        if 'Xcode' in cfg['generator'] :
            # find the Xcode project
            proj = glob.glob(build_dir + '/*.xcodeproj')
            subprocess.call('open {}'.format(proj[0]), shell=True)
        elif 'Visual Studio' in cfg['generator'] :
            # find the VisualStudio project file
            proj = glob.glob(build_dir + '/*.sln')
            subprocess.call('cmd /c start {}'.format(proj[0]), shell=True)
        else :
            log.error("don't know how to open a '{}' project".format(cfg['generator']))
    else :
        log.error("config '{}' not found".format(cfg_name))

#-------------------------------------------------------------------------------
def help() :
    """print help for verb 'open'"""
    log.info(log.YELLOW + 
            "fips open\n" 
            "fips open [config]\n" + log.DEF +
            "   open IDE for current or named config")

