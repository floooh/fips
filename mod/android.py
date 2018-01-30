"""Android SDK support"""

import os
import urllib
import zipfile
import subprocess

from mod import log, util 
from mod.tools import javac

tools_urls = {
    'win':      'https://dl.google.com/android/repository/sdk-tools-windows-3859397.zip',
    'osx':      'https://dl.google.com/android/repository/sdk-tools-darwin-3859397.zip',
    'linux':    'https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip'
}

tools_archives = {
    'win':      'sdk-tools-windows-3859397.zip',
    'osx':      'sdk-tools-darwin-3859397.zip',
    'linux':    'sdk-tools-linux-3859397.zip'
}

#-------------------------------------------------------------------------------
def get_sdk_dir(fips_dir) :
    return util.get_workspace_dir(fips_dir) + '/fips-sdks/android/'

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """check if the android sdk has been installed"""
    return os.path.isdir(get_sdk_dir(fips_dir))

#-------------------------------------------------------------------------------
def get_adb_path(fips_dir):
    return get_sdk_dir(fips_dir) + 'platform-tools/adb'

#-------------------------------------------------------------------------------
def get_tools_url() :
    return tools_urls[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_tools_archive_path(fips_dir):
    return get_sdk_dir(fips_dir) + '/' + tools_archives[util.get_host_platform()]

#-------------------------------------------------------------------------------
def install_package(fips_dir, pkg):
    log.colored(log.BLUE, '>>> install Android SDK package: {}'.format(pkg))
    sdkmgr_dir = get_sdk_dir(fips_dir) + 'tools/bin/'
    sdkmgr_path = sdkmgr_dir + 'sdkmanager'
    cmd = '{} --verbose {}'.format(sdkmgr_path, pkg)
    subprocess.call(cmd, cwd=sdkmgr_dir, shell=True)

#-------------------------------------------------------------------------------
def ensure_sdk_dirs(fips_dir) :
    if not os.path.isdir(get_sdk_dir(fips_dir)) :
        os.makedirs(get_sdk_dir(fips_dir))

#-------------------------------------------------------------------------------
def uncompress(fips_dir, path) :
    # the python zip module doesn't preserve the executable flags, so just
    # call unzip on Linux and OSX
    if util.get_host_platform() in ['osx', 'linux']:
        subprocess.call('unzip {}'.format(path), cwd=get_sdk_dir(fips_dir), shell=True)
    else:
        with zipfile.ZipFile(path, 'r') as archive:
            archive.extractall(get_sdk_dir(fips_dir))

#-------------------------------------------------------------------------------
def setup(fips_dir, proj_dir) :
    """setup the Android SDK and NDK"""
    log.colored(log.YELLOW, '=== setup Android SDK/NDK :')

    # first make sure that java is present, otherwise the Android
    # SDK setup will finish without errors, but is not actually usable
    if not javac.check_exists(fips_dir) :
        log.error("please install Java JDK (see './fips diag tools')")
    ensure_sdk_dirs(fips_dir)

    # download the command line tools archive
    tools_archive_path = get_tools_archive_path(fips_dir)
    tools_url = get_tools_url()
    log.info("downloading '{}'...".format(tools_url))
    urllib.urlretrieve(tools_url, tools_archive_path, util.url_download_hook)
    log.info("\nunpacking '{}'...".format(tools_archive_path))
    uncompress(fips_dir, tools_archive_path)

    # install the required SDK components through sdkmanager
    install_package(fips_dir, '"platforms;android-21"')
    install_package(fips_dir, '"build-tools;27.0.3"')
    install_package(fips_dir, 'platform-tools')
    install_package(fips_dir, 'ndk-bundle')

    log.colored(log.GREEN, "done.")
