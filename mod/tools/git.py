"""wrapper for some git commands"""

import re
import subprocess
from mod import log

name = 'git'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = "git not found in path, can't happen(?)"

#-------------------------------------------------------------------------------
def check_exists(fips_dir=None) :
    """test if git is in the path
    
    :returns:   True if git is in the path
    """
    try :
        subprocess.check_output(['git', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False

#-------------------------------------------------------------------------------
def clone(url, branch, name, cwd) :
    """git clone a remote git repo
    
    :param url:     the git url to clone from
    :param branch:  branch name (can be None)
    :param name:    the directory name to clone into
    :param cwd:     the directory where to run git
    :returns:       True if git returns successful
    """
    if check_exists() :
        cmd = 'git clone --recursive'
        if branch :
            cmd += ' --branch {} --single-branch --depth 10'.format(branch)
        cmd += ' {} {}'.format(url, name)
        res = subprocess.call(cmd, cwd=cwd, shell=True)
        return res == 0
    else :
        log.error("git not found, please run and fix './fips diag tools'")
        return False

#-------------------------------------------------------------------------------
def get_branches(proj_dir) :
    """get a dictionary with all local branch names of a git repo as keys,
    and their remote branch names as value
    
    :param proj_dir:    a git repo dir
    :returns:           dictionary of all local and remote branches
    """
    branches = {}
    try:
        output = subprocess.check_output('git branch -vv', cwd=proj_dir, shell=True)
        lines = output.splitlines()
        for line in lines :
            tokens = line[2:].split()
            local_branch = tokens[0]
            if re.compile("^\[.*(:|\])$").match(tokens[2]) :
                remote_branch = tokens[2][1:-1]
                branches[local_branch] = remote_branch
    except subprocess.CalledProcessError :
        log.error("failed to call 'git branch -vv'")
    return branches;

#-------------------------------------------------------------------------------
def has_uncommitted_files(proj_dir) :
    """check whether a git repo has uncommitted files

    :param proj_dir:    a git repo dir
    :returns:           True/False and output string
    """
    try :
        output = subprocess.check_output('git status -s', cwd=proj_dir, shell=True)
        if len(output) > 0 :
            return True, output
        else :
            return False, output
    except subprocess.CalledProcessError :
        log.error("failed to call 'git status -s'")
        return False, ''

#-------------------------------------------------------------------------------
def get_remote_rev(proj_dir, remote_branch) :
    """get the head rev of a remote branch

    :param proj_dir:        a git repo dir
    :param remote_branch:   remote branch (e.g. origin/master)
    :returns:               the revision string of the remote branch head or None
    """
    tokens = remote_branch.split('/')
    try :
        output = subprocess.check_output('git ls-remote {} {}'.format(tokens[0], tokens[1]), cwd=proj_dir, shell=True)
        # can return an empty string if the remote branch doesn't exist
        if output != '':
            return output.split()[0]
        else :
            return None
    except subprocess.CalledProcessError :
        log.error("failed to call 'git ls-remote'")
        return None

#-------------------------------------------------------------------------------
def get_local_rev(proj_dir, local_branch) :
    """get the head rev of a local branch

    :param proj_dir:        a git repo dir
    :param local_branch:    local branch name (e.g. master)
    :returns:               the revision string of the local branch head or None
    """
    try :
        output = subprocess.check_output('git rev-parse {}'.format(local_branch), cwd=proj_dir, shell=True)
        return output.rstrip()
    except subprocess.CalledProcessError :
        log.error("failed to call 'git rev-parse'")
        return None
    
#-------------------------------------------------------------------------------
def check_out_of_sync(proj_dir) :
    """check through all branches of the git repo in proj_dir and
    returns an array of all branches that are out-of-sync with their
    remote branches (either have unpushed local changes, or un-pulled
    remote changes)

    :param proj_dir:    a git repo directory
    :returns:           array with branch names that are out-of-sync
    """
    if not check_exists() :
        log.error("git not found, please run and fix './fips diag tools'")
        return False

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
    if not branches :
        log.warn("'{}' no remote branches found".format(proj_dir))
    for local_branch in branches :
        remote_branch = branches[local_branch]
        remote_rev = get_remote_rev(proj_dir, remote_branch)

        # remote_rev can be None if the remote branch doesn't exists,
        # this is not an error
        if remote_rev :
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

#-------------------------------------------------------------------------------
def check_branch_out_of_sync(proj_dir, branch) :
    """check if a single branch is out of sync with remote repo"""
    if not check_exists() :
        log.error("git not found, please run and fix './fips diag tools'")
        return False

    out_of_sync = False
    remote_branches = get_branches(proj_dir)
    local_rev = get_local_rev(proj_dir, branch)
    if branch in remote_branches :
        remote_rev = get_remote_rev(proj_dir, remote_branches[branch])
        out_of_sync = remote_rev != local_rev
    else :
        log.warn("'{}' no remote branch found for '{}'".format(proj_dir, branch))

    return out_of_sync
