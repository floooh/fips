"""Android SDK support"""

import os
import urllib
import zipfile
import subprocess

from mod import log, util 
from mod.tools import java

sdk_urls = {
    'win' :     'http://dl.google.com/android/android-sdk_r22.6.2-windows.zip',
    'osx' :     'http://dl.google.com/android/android-sdk_r22.6.2-macosx.zip',
    'linux' :   'http://dl.google.com/android/android-sdk_r22.6.2-linux.tgz'
}

sdk_archives = {
    'win' :     'android-sdk_r22.6.2-windows.zip',
    'osx' :     'android-sdk_r22.6.2-macosx.zip',
    'linux' :   'android-sdk_r22.6.2-linux.tgz'
}

sdk_paths = { 
    'win' :     'android-sdk-windows',
    'osx' :     'android-sdk-macosx',
    'linux' :   'android-sdk-linux'    
}

ndk_urls = {
    'win' :     'http://dl.google.com/android/ndk/android-ndk-r9d-windows-x86.zip',
    'osx' :     'http://dl.google.com/android/ndk/android-ndk-r9d-darwin-x86_64.tar.bz2',
    'linux' :   'http://dl.google.com/android/ndk/android-ndk-r9d-linux-x86_64.tar.bz2'
}

ndk_archives = {
    'win' :     'android-ndk-r9d-windows-x86.zip',
    'osx' :     'android-ndk-r9d-darwin-x86_64.tar.bz2',
    'linux' :   'android-ndk-r9d-linux-x86_64.tar.bz2'
}

#-------------------------------------------------------------------------------
def get_sdk_url() :
    return sdk_urls[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_ndk_url() :
    return ndk_urls[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_sdk_dir(fips_dir) :
    return util.get_workspace_dir(fips_dir) + '/fips-sdks/' + util.get_host_platform()

#-------------------------------------------------------------------------------
def get_androidsdk_dir(fips_dir) :
    return get_sdk_dir(fips_dir) + '/' + sdk_paths[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_androidndk_dir(fips_dir) :
    return get_sdk_dir(fips_dir) + '/android-ndk-r9d'

#-------------------------------------------------------------------------------
def get_androidsdk_archive_path(fips_dir) :
    return get_sdk_dir(fips_dir) + '/' + sdk_archives[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_androidndk_archive_path(fips_dir) :
    return get_sdk_dir(fips_dir) + '/' + ndk_archives[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_adb_path(fips_dir) :
    return get_androidsdk_dir(fips_dir) + '/platform-tools/adb'

#-------------------------------------------------------------------------------
def ensure_sdk_dirs(fips_dir) :
    if not os.path.isdir(get_sdk_dir(fips_dir)) :
        os.makedirs(get_sdk_dir(fips_dir))

#-------------------------------------------------------------------------------
def uncompress(fips_dir, path) :
    if '.zip' in path :
        with zipfile.ZipFile(path, 'r') as archive:
            archive.extractall(get_sdk_dir(fips_dir))
    elif '.bz2' or '.tgz' in path :
        # note: for some reason python's tarfile
        # module cannot completely unpack the 
        # Android NDK tar.gz2 file (tested on OSX with python 2.7),
        # so fall back to command line tar
        subprocess.call('tar -xvf {}'.format(path), cwd=get_sdk_dir(fips_dir), shell=True)

#-------------------------------------------------------------------------------
def update_android_sdk(fips_dir, proj_dir) :
    # FIXME: hardcoded version numbers should be configurable
    if util.get_host_platform() == 'win' :
        cmd = '{}/tools/android.bat update sdk -f -u --all --filter tools,platform-tools,build-tools-19.1.0,android-19'.format(get_androidsdk_dir(fips_dir))
    else :
        cmd = 'sh {}/tools/android update sdk -f -u --all --filter tools,platform-tools,build-tools-19.1.0,android-19'.format(get_androidsdk_dir(fips_dir))
    print(cmd)
    subprocess.call(cmd, cwd=fips_dir, shell=True)

#-------------------------------------------------------------------------------
def setup(fips_dir, proj_dir) :
    """setup the Android SDK and NDK"""
    log.colored(log.YELLOW, '=== setup Android SDK/NDK :')

    # first make sure that java is present, otherwise the Android
    # SDK setup will finish without errors, but is not actually usable
    if not java.check_exists(fips_dir) :
        log.error("please install java first (see './fips diag tools')")

    ensure_sdk_dirs(fips_dir)

    # download and setup the Android SDK
    sdk_archive_path = get_androidsdk_archive_path(fips_dir)
    if not os.path.isfile(sdk_archive_path) :        
        sdk_url = get_sdk_url()
        log.info("downloading '{}'...".format(sdk_url))
        urllib.urlretrieve(sdk_url, sdk_archive_path, util.url_download_hook)
    else :
        log.info("'{}' already exists".format(sdk_archive_path))
    log.info("\nunpacking '{}'...".format(sdk_archive_path))
    uncompress(fips_dir, sdk_archive_path)
    log.info("downloading additional SDK files...")
    update_android_sdk(fips_dir, proj_dir)

    # download the Android NDK
    ndk_archive_path = get_androidndk_archive_path(fips_dir)
    if not os.path.isfile(ndk_archive_path) :
        ndk_url = get_ndk_url()
        log.info("downloading '{}'...".format(ndk_url))
        urllib.urlretrieve(ndk_url, ndk_archive_path, util.url_download_hook)
    else :
        log.info("'{}' already exists".format(ndk_archive_path))
    log.info("\nunpacking '{}'...".format(ndk_archive_path))
    uncompress(fips_dir, ndk_archive_path)

    log.colored(log.GREEN, "done.")

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """check if the android sdk/ndk has been installed"""
    return os.path.isdir(get_androidsdk_dir(fips_dir)) and os.path.isdir(get_androidndk_dir(fips_dir))
