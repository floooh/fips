"""wrapper for some git commands"""

import subprocess

name = 'git'
platforms = ['linux', 'osx', 'win']

#-------------------------------------------------------------------------------
def check_exists() :
    """test if git is in the path
    
    :returns:   True if git is in the path
    """
    try :
        subprocess.check_output(['git', '--version'])
        return True
    except OSError:
        return False

#-------------------------------------------------------------------------------
def clone(url, name, cwd) :
    """git clone a remote git repo
    
    :param url:     the git url to clone from
    :param name:    the directory name to clone into
    :param cwd:     the directory where to run git
    :returns:       True if git returns successful
    """
    res = subprocess.call(['git', 'clone', url, name], cwd=cwd)
    return res == 0


