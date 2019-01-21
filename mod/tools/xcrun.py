""" wrapper for xcrun (helper tool on OSX) """
import subprocess

name = 'xcrun'
platforms = ['osx']
optional = False
not_found = 'please install Xcode and Xcode cmd line tools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if xcrun is in the path
    
    :returns:   True if xcrun is in the path
    """
    try:
        subprocess.check_output(['xcrun', '-version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#------------------------------------------------------------------------------
def get_macos_sdk_sysroot():
    try:
        return subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path']).decode('utf-8').rstrip()
    except (OSError, subprocess.CalledProcessError):
        return None

#------------------------------------------------------------------------------
def get_ios_sdk_sysroot():
    try:
        return subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path']).decode('utf-8').rstrip()
    except (OSError, subprocess.CalledProcessError):
        return None
