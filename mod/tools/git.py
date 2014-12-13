"""wrapper for some git commands"""

import subprocess

name = 'git'
platforms = ['Linux', 'Darwin', 'Windows']

#-------------------------------------------------------------------------------
def check_exists() :
    """test if git is in the path"""
    try :
        subprocess.check_output(['git', '--version'])
        return True
    except OSError:
        return False

#-------------------------------------------------------------------------------
def clone(url, name, cwd) :
    """git clone a remote git repo
    
    url     -- the git url to clone from
    name    -- the directory name to clone into
    cwd     -- the directory where to run git
    """
    res = subprocess.call(['git', 'clone', url, name], cwd=cwd)
    return res == 0


