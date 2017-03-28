"""emscripten SDK support"""

import os
import urllib
import zipfile
import subprocess

from mod import log, util

archives = {
    'win': 'emsdk-portable.zip',
    'osx': 'emsdk-portable.tar.gz',
    'linux': 'emsdk-portable.tar.gz'
}

urls = {
    'win':      'http://s3.amazonaws.com/mozilla-games/emscripten/releases/{}'.format(archives['win']),
    'osx' :     'http://s3.amazonaws.com/mozilla-games/emscripten/releases/{}'.format(archives['osx']),
    'linux' :   'http://s3.amazonaws.com/mozilla-games/emscripten/releases/{}'.format(archives['linux'])
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
def get_emsdk_dir(fips_dir) :
    """return the emscripten SDK path (emsdk-portable)"""
    return get_sdk_dir(fips_dir) + '/emsdk-portable'

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
def finish(sdk_dir, version_tag) :
    """finish setting up the emscripten SDK"""
    if util.get_host_platform() == 'win':
        # on Windows use a stable SDK version which doesn't require clang to be compiled
        subprocess.call(args='emsdk.bat update', cwd=sdk_dir, shell=True)
        subprocess.call(args='emsdk.bat install {}'.format(version_tag), cwd=sdk_dir, shell=True)
        subprocess.call(args='emsdk.bat activate --embedded {}'.format(version_tag), cwd=sdk_dir, shell=True)
    else :
        subprocess.call(args='./emsdk update', cwd=sdk_dir, shell=True)
        subprocess.call(args='./emsdk install {}'.format(version_tag), cwd=sdk_dir, shell=True)
        subprocess.call(args='./emsdk activate --embedded {}'.format(version_tag), cwd=sdk_dir, shell=True)

#-------------------------------------------------------------------------------
def setup(fips_dir, proj_dir, version) :
    """setup the emscripten SDK from scratch

    Version is smth like 'incoming' or '1.37.9', the actual emsdk 
    version tag will be sdk-[version]-64bit
    """
    if version is None:
        version = 'incoming'
    version_tag = 'sdk-{}-64bit'.format(version)
    log.colored(log.YELLOW, '=== setup emscripten SDK ({}):'.format(version_tag))

    ensure_sdk_dirs(fips_dir)

    # download SDK archive
    if not os.path.isfile(get_archive_path(fips_dir)) :
        log.info("downloading '{}'...".format(get_archive_name()))
        urllib.urlretrieve(get_sdk_url(), get_archive_path(fips_dir), util.url_download_hook)
    else :
        log.info("'{}' already exists".format(get_archive_name()))

    # uncompress SDK archive
    log.info("uncompressing '{}'...".format(get_archive_name()))
    uncompress(get_archive_path(fips_dir), get_sdk_dir(fips_dir), 'emsdk-portable')

    # setup SDK
    log.info("setup emscripten SDK...")
    finish(get_emsdk_dir(fips_dir), version_tag)

    # write version tag, to a file which will be loaded by the cmake
    # toolchain file later
    version_path = '{}/fips_emsdk_version.txt'.format(get_emsdk_dir(fips_dir))
    log.info("write version tag to '{}'".format(version_path))
    with open(version_path, "w") as f:
        f.write(version)
    
    log.colored(log.GREEN, "done.")

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """check if the emscripten sdk has been installed"""
    return os.path.isdir(get_emsdk_dir(fips_dir))

    



