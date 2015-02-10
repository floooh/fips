""" NaCl SDK support"""

import os
import stat
import urllib
import zipfile
import subprocess

from mod import log, util

#-------------------------------------------------------------------------------
def get_sdk_url() :
    """returns the SDK download URL"""
    return 'http://storage.googleapis.com/nativeclient-mirror/nacl/nacl_sdk/nacl_sdk.zip'

#-------------------------------------------------------------------------------
def get_sdk_dir(fips_dir) :
    """return the platform-specific SDK dir"""
    return util.get_workspace_dir(fips_dir) + '/fips-sdks/' + util.get_host_platform()

#-------------------------------------------------------------------------------
def get_naclsdk_dir(fips_dir) :
    """return the NaCl SDK path"""
    return get_sdk_dir(fips_dir) + '/nacl_sdk'

#-------------------------------------------------------------------------------
def get_archive_path(fips_dir) :
    """return path to downloaded archive"""
    return get_sdk_dir(fips_dir) + '/nacl_sdk.zip'

#-------------------------------------------------------------------------------
def ensure_sdk_dirs(fips_dir) :
    """make sure the sdk dir exists"""
    naclsdk_dir = get_naclsdk_dir(fips_dir)
    if not os.path.isdir(naclsdk_dir) :
        os.makedirs(naclsdk_dir)

#-------------------------------------------------------------------------------
def uncompress(fips_dir, path) :
    """uncompress the SDK archive"""
    with zipfile.ZipFile(path, 'r') as archive:
        archive.extractall(get_sdk_dir(fips_dir))

#-------------------------------------------------------------------------------
def update_nacl_sdk(fips_dir) :
    """run the actual nacl_sdk update process"""
    nacl_sdk = '{}/naclsdk'.format(get_naclsdk_dir(fips_dir))
    os.chmod(nacl_sdk, 0o744)
    cmd = '{} install --force pepper_canary'.format(nacl_sdk)
    subprocess.call(cmd, cwd=get_naclsdk_dir(fips_dir), shell=True)
    
#-------------------------------------------------------------------------------
def setup(fips_dir, proj_dir) :
    """main setup function"""
    log.colored(log.YELLOW, '=== setup NaCl SDK:')

    ensure_sdk_dirs(fips_dir)

    # download SDK archive
    if not os.path.isfile(get_archive_path(fips_dir)) :
        log.info("downloading...")
        urllib.urlretrieve(get_sdk_url(), get_archive_path(fips_dir), util.url_download_hook)
    else :
        log.info("'nacl_sdk.zip' already exists")
    
    # uncompress SDK archive
    log.info("unpacking...")
    uncompress(fips_dir, get_archive_path(fips_dir))

    # setup SDK
    log.info("setup NaCl SDK...")
    update_nacl_sdk(fips_dir)

    log.colored(log.GREEN, "done.")

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """check if nacl sdk is installed"""
    return os.path.isdir(get_naclsdk_dir(fips_dir))
    
