"""wrapper for some git commands"""

import subprocess
from mod import log

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

#-------------------------------------------------------------------------------
def get_branches(proj_dir) :
    """get a dictionary with all local branch names of a git repo as keys,
    and their remote branch names as value
    
    :param proj_dir:    a git repo dir
    :returns:           dictionary of all local and remote branches
    """
    branches = {}
    output = subprocess.check_output(['git', 'branch', '-vv'], cwd=proj_dir)
    lines = output.splitlines()
    for line in lines :
        tokens = line[2:].split()
        local_branch = tokens[0]
        remote_branch = tokens[2][1:-1]
        branches[local_branch] = remote_branch
    return branches

#-------------------------------------------------------------------------------
def has_uncommitted_files(proj_dir) :
    """check whether a git repo has uncommitted files

    :param proj_dir:    a git repo dir
    :returns:           True/False and output string
    """
    output = subprocess.check_output(['git', 'status', '-s'], cwd=proj_dir)
    if len(output) > 0 :
        return True, output
    else :
        return False, output

#-------------------------------------------------------------------------------
def get_remote_rev(proj_dir, remote_branch) :
    """get the head rev of a remote branch

    :param proj_dir:        a git repo dir
    :param remote_branch:   remote branch (e.g. origin/master)
    :returns:               the revision string of the remote branch head
    """
    tokens = remote_branch.split('/')
    output = subprocess.check_output(['git', 'ls-remote', tokens[0], tokens[1]], cwd=proj_dir)
    return output.split()[0]

#-------------------------------------------------------------------------------
def get_local_rev(proj_dir, local_branch) :
    """get the head rev of a local branch

    :param proj_dir:        a git repo dir
    :param local_branch:    local branch name (e.g. master)
    :returns:               the revision string of the local branch head
    """
    output = subprocess.check_output(['git', 'rev-parse', local_branch], cwd=proj_dir)
    return output.rstrip()
    
#-------------------------------------------------------------------------------
def check_out_of_sync(proj_dir) :
    """check through all branches of the git repo in proj_dir and
    returns an array of all branches that are out-of-sync with their
    remote branches (either have unpushed local changes, or un-pulled
    remote changes)

    :param proj_dir:    a git repo directory
    :returns:           array with branch names that are out-of-sync
    """
    out_of_sync = False

    # first check whether there are uncommitted changes
    status, status_output = has_uncommitted_files(proj_dir)
    if status :
        out_of_sync = True
        log.warn("'{}' has uncommitted changes:".format(proj_dir))
        log.info(status_output)

    # check whether local and remote branch are out of sync
    branches_out_of_sync = False
    branches = get_branches(proj_dir)
    for local_branch in branches :
        remote_branch = branches[local_branch]
        remote_rev = get_remote_rev(proj_dir, remote_branch)
        local_rev = get_local_rev(proj_dir, local_branch)
        if remote_rev != local_rev :
            out_of_sync = True
            if not branches_out_of_sync:
                # only show this once
                log.warn("'{}' branches out of sync:".format(proj_dir))
                branches_out_of_sync = True
            log.info("  {}: {}".format(local_branch, local_rev))
            log.info("  {}: {}".format(remote_branch, remote_rev))
                    
    return out_of_sync

