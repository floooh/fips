"""
    Backend code for the new 'emsdk' verb.

    This provides a more flexible wrapper for the emsdk emscripten SDK
    installer.
    
    Changes to the previous approach:

    - emsdk is installed via git
    - things like updating or switching SDK versions work by directly
      forwarding commands to the emsdk script
    - it's possible to query the active SDK root directory for forwarding
      to cmake (the emscripten cmake toolchain file will no longer
      be hardwired to a specific version)
"""

import os, stat, sys, subprocess, shutil
from mod import log, util
from mod.tools import git

EMSDK_URL = "https://github.com/emscripten-core/emsdk.git"
EMSDK_DEFAULT_VERSION = 'latest'

# this is an error callback function for shutil.rmtree to make
# read-only files writable after rmtree failed to delete them
#
# from: https://docs.python.org/3.5/library/shutil.html#rmtree-example
#
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

#-------------------------------------------------------------------------------
def get_sdkroot_dir(fips_dir):
    return util.get_workspace_dir(fips_dir) + '/fips-sdks'

#-------------------------------------------------------------------------------
def sdkroot_exists(fips_dir):
    sdkroot_dir = get_sdkroot_dir(fips_dir)
    return os.path.isdir(sdkroot_dir)

#-------------------------------------------------------------------------------
def make_dirs(fips_dir):
    if not sdkroot_exists(fips_dir):
        os.makedirs(get_sdkroot_dir(fips_dir))

#-------------------------------------------------------------------------------
def get_emsdk_dir(fips_dir):
    return get_sdkroot_dir(fips_dir) + '/emsdk'

#-------------------------------------------------------------------------------
def emsdk_dir_exists(fips_dir):
    emsdk_dir = get_emsdk_dir(fips_dir)
    return os.path.isdir(emsdk_dir)

#-------------------------------------------------------------------------------
def get_emsdk_path(fips_dir):
    emsdk_script = 'emsdk.bat' if util.get_host_platform() == 'win' else 'emsdk'
    emsdk_path = get_emsdk_dir(fips_dir) + '/' + emsdk_script
    return emsdk_path

#-------------------------------------------------------------------------------
def check_exists(fips_dir):
    emsdk_path = get_emsdk_path(fips_dir)
    return os.path.isfile(emsdk_path)

#-------------------------------------------------------------------------------
def get_em_config(fips_dir):
    # returns the path to the local .emscripten file
    return get_emsdk_dir(fips_dir) + '/.emscripten'

#-------------------------------------------------------------------------------
def run(fips_dir, cmdline):
    if not check_exists(fips_dir):
        log.error("emsdk script not found at '{}', please run './fips emsdk install'".format(get_emsdk_path(fips_dir)))
    emsdk_path = get_emsdk_path(fips_dir)
    emsdk_dir = get_emsdk_dir(fips_dir)
    cmd = '{} {}'.format(emsdk_path, cmdline)
    subprocess.call(cmd, cwd=emsdk_dir, shell=True)

#-------------------------------------------------------------------------------
def clone_or_update_emsdk(fips_dir):
    # returns True on success
    emsdk_dir = get_emsdk_dir(fips_dir)
    if emsdk_dir_exists(fips_dir):
        log.colored(log.YELLOW, "=== updating emscripten SDK at '{}'".format(emsdk_dir))
        return git.update_force_and_ignore_local_changes(emsdk_dir)
    else:
        log.colored(log.YELLOW, "=== cloning emscripten SDK to '{}'".format(emsdk_dir))
        make_dirs(fips_dir)
        sdkroot_dir = get_sdkroot_dir(fips_dir)
        return git.clone(EMSDK_URL, None, 1, "emsdk", sdkroot_dir)

#-------------------------------------------------------------------------------
def list(fips_dir):
    run(fips_dir, "list")

#-------------------------------------------------------------------------------
def activate(fips_dir, emsdk_version):
    if emsdk_version is None:
        emsdk_version = EMSDK_DEFAULT_VERSION
    log.colored(log.YELLOW, "=== activating emscripten SDK version '{}'".format(emsdk_version))
    run(fips_dir, "activate --embedded {}".format(emsdk_version))

#-------------------------------------------------------------------------------
def install(fips_dir, emsdk_version):
    if not clone_or_update_emsdk(fips_dir):
        log.error('Failed to install or update emscripten SDK')
    if emsdk_version is None:
        emsdk_version = EMSDK_DEFAULT_VERSION
    log.colored(log.YELLOW, "=== installing emscripten tools for '{}'".format(emsdk_version))
    run(fips_dir, "install --shallow --disable-assertions {}".format(emsdk_version))
    activate(fips_dir, emsdk_version)

#-------------------------------------------------------------------------------
def remove_old_sdks(fips_dir):
    # this checks for any "old" SDKs and removes them
    old_sdk_path = get_sdkroot_dir(fips_dir) + '/' + util.get_host_platform()
    if os.path.isdir(old_sdk_path):
        if util.confirm(log.RED + "Delete obsolete emscripten SDK in '{}'?".format(old_sdk_path) + log.DEF):
            log.info("Deleting '{}'...".format(old_sdk_path))
            shutil.rmtree(old_sdk_path, onerror=remove_readonly)
        else:
            log.info("'No' selected, nothing deleted")

#-------------------------------------------------------------------------------
def uninstall(fips_dir):
    emsdk_dir = get_emsdk_dir(fips_dir)
    log.colored(log.YELLOW, "=== uninstalling emscripten SDK".format(emsdk_dir))
    # check for any "old" SDK installation
    remove_old_sdks(fips_dir)
    if emsdk_dir_exists(fips_dir):
        if util.confirm(log.RED + "Delete emsdk directory at '{}'?".format(emsdk_dir) + log.DEF):
            log.info("Deleting '{}'...".format(emsdk_dir))
            shutil.rmtree(emsdk_dir, onerror=remove_readonly)
        else:
            log.info("'No' selected, nothing deleted")
    else:
        log.warn('emscripten SDK is not installed, nothing to do')

#-------------------------------------------------------------------------------
def parse_config(fips_dir):
    # evaluates the .emscripten config file and returns key/value pairs of content
    config = {}
    config_path = get_em_config(fips_dir)
    os.environ['EM_CONFIG'] = config_path
    try:
        with open(config_path, 'r') as f:
            config_text = f.read()
            exec(config_text, config)
    except Exception as e:
        log.error("error in evaluating .emscripten file at '{}' with '{}'".format(config_path, str(e)))
    return config

#-------------------------------------------------------------------------------
def show_config(fips_dir):
    emsdk_config = parse_config(fips_dir)
    for key, value in emsdk_config.items():
        if key not in ['__builtins__', 'emsdk_path', 'os']:
            log.info('{}: {}'.format(key, value))

#-------------------------------------------------------------------------------
def get_emscripten_root(fips_dir):
    # returns the path where the emcc, em++ etc scripts are located
    emsdk_config = parse_config(fips_dir)
    if 'EMSCRIPTEN_ROOT' in emsdk_config:
        # older SDKs
        return emsdk_config['EMSCRIPTEN_ROOT']
    else:
        # new SDKs
        return emsdk_config['BINARYEN_ROOT'] + '/emscripten'
