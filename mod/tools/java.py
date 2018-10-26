"""wrapper for java, only check_exists"""
import subprocess
import re

name = 'java'
platforms = ['osx', 'linux', 'win']
optional = True
not_found = "version 8 required for Android development, installed with the Java JDK"

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    try :
        res = subprocess.check_output(['java', '-version'],
            stderr=subprocess.STDOUT,
            universal_newlines=True) # return string not binary for python 2/3 compatibility
    except (OSError, subprocess.CalledProcessError) :
        return False
    ver = re.search("version \"([^\\s]+)\"", res)
    if not ver or not ver.group(1).startswith('1.8') :
        return False
    return True

