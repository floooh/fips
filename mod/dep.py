"""functions for external dependencies"""

import os
import yaml
from mod import log, util, project, registry
from mod.tools import git

#-------------------------------------------------------------------------------
def get_imports(proj_dir) :
    """get the imports from the fips.yml file in the project

    :param proj_dir:    the project directory
    :returns:           dictionary object with imports (can be empty)
    """
    imports = {}
    if project.is_valid_project_dir(proj_dir) :
        path = proj_dir + '/fips.yml'
        f = open(path, 'r')
        dic = yaml.load(f)
        if dic and 'imports' in dic :
            imports = dic['imports']
    else :
        log.error("{} is not a valid project dir".format(proj_dir))
    return imports

#-------------------------------------------------------------------------------
def _rec_fetch_imports(fips_dir, proj_dir, handled) :
    """internal recursive function to fetch project imports,
    keeps an array of already handled dirs to break cyclic dependencies

    :param proj_dir:    current project directory
    :param handled:     array of already handled dirs
    :returns:           updated array of handled dirs
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    if proj_name not in handled :
        handled.append(proj_name)

        imports = get_imports(proj_dir)
        for dep in imports:
            # dep can be a project name or direct git url,
            # if project name, lookup url in fips registry
            dep_url = registry.get_url(fips_dir, dep)
            if not git.is_valid_url(dep_url) :
                log.error("'{}' can't be resolved to a git url (in project '{}')".format(dep_url, proj_name))

            dep_proj_name = util.get_project_name_from_url(dep_url)
            if dep_proj_name not in handled:
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                log.colored(log.YELLOW, "=== depedency: '{}':".format(dep_proj_name))
                dep_ok = False
                if not os.path.isdir(dep_proj_dir) :
                    # directory did not exist, do a fresh git clone
                    if git.clone(dep_url, dep_proj_name, ws_dir) :
                        dep_ok = True
                    else :
                        log.error('failed to git clone {} into {}'.format(dep_url, dep_proj_dir))
                else :
                    # directory already exists, issue warnings if it out-of-sync
                    # with it's remote, but never try to resolve this automatically
                    log.info("dir '{}' already exists, doing out-of-sync check:".format(dep_proj_dir))
                    if git.check_out_of_sync(dep_proj_dir) :
                        log.warn("dir '{}' is out of sync, skipping imports".format(dep_proj_dir))
                    else :
                        dep_ok = True
                        log.info("dir '{}' is up to date".format(dep_proj_dir))

                # recuse
                if dep_ok :
                    handled = _rec_fetch_imports(fips_dir, dep_proj_dir, handled)

    # done, return the new handled array
    return handled

#-------------------------------------------------------------------------------
def fetch_imports(fips_dir, proj_dir) :
    """recursively git-clone the imports of a project, NOTE: existing
    repos will never be updated, but a warning will be issued if they
    are out-of-sync with their remotes

    :param proj_dir:    existing project directory
    """
    _rec_fetch_imports(fips_dir, proj_dir, [])

