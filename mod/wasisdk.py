"""
    Manage the wasisdk.
"""

import sys, os, tarfile, shutil
from mod import log, util

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve

dir_name = 'wasi-sdk-14.0'

urls = {
    'linux': 'https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-14/wasi-sdk-14.0-linux.tar.gz',
    'osx':   'https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-14/wasi-sdk-14.0-macos.tar.gz',
    'win':   'https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-14/wasi-sdk-14.0-mingw.tar.gz'
}

def get_sdk_dir(fips_dir):
    return util.get_workspace_dir(fips_dir) + '/fips-sdks/wasisdk'

def check_exists(fips_dir):
    return os.path.isdir(get_sdk_dir(fips_dir))

def get_url():
    return urls[util.get_host_platform()]

def get_archive_path(fips_dir):
    return get_sdk_dir(fips_dir) + '/' + os.path.basename(get_url())

def get_wasisdk_root(fips_dir):
    return get_sdk_dir(fips_dir) + '/' + dir_name 

def sdk_dir_exists(fips_dir):
    return os.path.isdir(get_sdk_dir(fips_dir))

def ensure_sdk_dirs(fips_dir) :
    if not sdk_dir_exists(fips_dir):
        os.makedirs(get_sdk_dir(fips_dir))

def install(fips_dir):
    log.colored(log.YELLOW, '=== installing WASI SDK:')
    ensure_sdk_dirs(fips_dir)
    sdk_url = get_url()
    archive_path = get_archive_path(fips_dir)
    log.info("downloading '{}'...".format(sdk_url))
    urlretrieve(sdk_url, archive_path, util.url_download_hook)
    log.info("\nunpacking '{}'...".format(archive_path))
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path = get_sdk_dir(fips_dir))

def uninstall(fips_dir):
    log.colored(log.YELLOW, "=== uninstalling WASI SDK")
    if sdk_dir_exists(fips_dir):
        sdk_dir = get_sdk_dir(fips_dir)
        if util.confirm(log.RED + "Delete directory '{}?".format(sdk_dir) + log.DEF):
            log.info("Deleting '{}'...".format(sdk_dir))
            shutil.rmtree(sdk_dir)
        else:
            log.info("'No' selected, nothing deleted")
    else:
        log.warn("WASI SDK is not installed, nothing to do")
