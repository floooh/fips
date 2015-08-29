"""emscripten SDK support"""

import os
import urllib
import zipfile
import subprocess

from mod import log, util

archives = {
    'win': 'emsdk-1.34.1-portable-64bit.zip',
    'osx': 'emsdk-portable.tar.gz',
    'linux': 'emsdk-portable.tar.gz'
}

urls = {
    'win':      'http://s3.amazonaws.com/mozilla-games/emscripten/releases/emsdk-1.34.1-portable-64bit.zip',
    'osx' :     'http://s3.amazonaws.com/mozilla-games/emscripten/releases/emsdk-portable.tar.gz',
    'linux' :   'http://s3.amazonaws.com/mozilla-games/emscripten/releases/emsdk-portable.tar.gz'
}

# define SDK version, note that the right version must also
# be set in the emscripten.toolchain.cmake file!
sdk_version = {
    # on Windows, use a stable SDK version which has a pre-compiled clang
    'win': 'sdk-1.34.1-64bit',
    # on Linux and OSX, use the bleeding-edge SDK version
    'osx': 'sdk-incoming-64bit',
    'linux': 'sdk-incoming-64bit'
}

#-------------------------------------------------------------------------------
def get_sdk_url() :
    """lookup SDK url for this host platform"""
    return urls[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_sdk_dir(fips_dir) :
    """return the platform-specific SDK dir"""
    return util.get_workspace_dir(fips_dir) + '/fips-sdks/' + util.get_host_platform()

#-------------------------------------------------------------------------------
def get_sdk_version() :
    return sdk_version[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_emsdk_dir(fips_dir) :
    """return the emscripten SDK path (emsdk_portable)"""
    return get_sdk_dir(fips_dir) + '/emsdk_portable'

#-------------------------------------------------------------------------------
def get_archive_name() :
    """return name of sdk archive"""
    return archives[util.get_host_platform()]

#-------------------------------------------------------------------------------
def get_archive_path(fips_dir) :
    """return path to sdk archive"""
    return get_sdk_dir(fips_dir) + '/' + get_archive_name() 

#-------------------------------------------------------------------------------
def ensure_sdk_dirs(fips_dir) :
    """make sure the sdk dir exists"""
    emsdk_dir = get_emsdk_dir(fips_dir)
    if not os.path.isdir(emsdk_dir) :
        os.makedirs(emsdk_dir)

#-------------------------------------------------------------------------------
def uncompress(src_path, dst_path, zip_dir_name) :
    if '.zip' in src_path :
        with zipfile.ZipFile(src_path, 'r') as archive:
            archive.extractall(dst_path + '/' + zip_dir_name)
    elif '.tgz' or '.bz2' in path :
        subprocess.call('tar -xvf {}'.format(src_path), cwd=dst_path, shell=True)

#-------------------------------------------------------------------------------
def finish(sdk_dir) :
    """finish setting up the emscripten SDK

    FIXME: the used SDK version should be configurable!
    """
    if util.get_host_platform() == 'win' :
        # on Windows use a stable SDK version which doesn't require clang to be compiled
        subprocess.call(args='emsdk.bat update', cwd=sdk_dir, shell=True)
        subprocess.call(args='emsdk.bat install {}'.format(get_sdk_version()), cwd=sdk_dir, shell=True)
        subprocess.call(args='emsdk.bat activate --embedded {}'.format(get_sdk_version()), cwd=sdk_dir, shell=True)
    else :
        subprocess.call(args='./emsdk update', cwd=sdk_dir, shell=True)
        subprocess.call(args='./emsdk install {}'.format(get_sdk_version()), cwd=sdk_dir, shell=True)
        subprocess.call(args='./emsdk activate --embedded {}'.format(get_sdk_version()), cwd=sdk_dir, shell=True)

#-------------------------------------------------------------------------------
def setup(fips_dir, proj_dir) :
    """setup the emscripten SDK from scratch"""
    log.colored(log.YELLOW, '=== setup emscripten SDK:')

    ensure_sdk_dirs(fips_dir)

    # download SDK archive
    if not os.path.isfile(get_archive_path(fips_dir)) :
        log.info("downloading '{}'...".format(get_archive_name()))
        urllib.urlretrieve(get_sdk_url(), get_archive_path(fips_dir), util.url_download_hook)
    else :
        log.info("'{}' already exists".format(get_archive_name()))

    # uncompress SDK archive
    log.info("uncompressing '{}'...".format(get_archive_name()))
    uncompress(get_archive_path(fips_dir), get_sdk_dir(fips_dir), 'emsdk_portable')

    # setup SDK
    log.info("setup emscripten SDK...")
    finish(get_emsdk_dir(fips_dir))

    log.colored(log.GREEN, "done.")

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """check if the emscripten sdk has been installed"""
    return os.path.isdir(get_emsdk_dir(fips_dir))

    



