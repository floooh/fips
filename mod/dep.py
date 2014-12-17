"""functions for external dependencies"""

import os
from collections import OrderedDict
from mod import log, util, project, registry
from mod.tools import git

#-------------------------------------------------------------------------------
def get_imports(proj_dir) :
    """get the imports from the fips.yml file in proj_dir

    :param proj_dir:    the project directory
    :returns:           dictionary object with imports (can be empty)
    """
    project.ensure_valid_project_dir(proj_dir)
    imports = {}
    dic = util.load_fips_yml(proj_dir)
    if 'imports' in dic :
        imports = dic['imports']
    return imports

#-------------------------------------------------------------------------------
def get_exports(proj_dir) :
    """get the exports from the fips.yml file in proj_dir

    :param proj_dir:    the project directory
    :returns:           dictionary object with exports (can be empty)
    """
    project.ensure_valid_project_dir(proj_dir)
    exports = {}
    dic = util.load_fips_yml(proj_dir)
    if 'exports' in dic :
        exports = dic['exports']
    return exports

#-------------------------------------------------------------------------------
def _rec_get_all_imports_exports(fips_dir, proj_dir, proj_url, result) :
    """recursively get all imported projects, their exported and
    imported modules in a dictionary object:
        
        project-1:
            url:    git-url (not valid for first, top-level project)
            exports:
                mod: dir
                mod: dir
                ...
            imports:
                project or url:
                    import-name: local-name
                    import-name: local-name
                ...
        ...

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param result:      in/out current result
    :returns:           bool success, and modified result dictionary
    """
    success = True
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    if proj_name not in result :

        result[proj_name] = {}
        result[proj_name]['imports'] = get_imports(proj_dir)
        result[proj_name]['exports'] = get_exports(proj_dir)
        result[proj_name]['url'] = proj_url

        for dep in result[proj_name]['imports'] :
            # dep can be a project name or a direct git url,
            # if project name, lookup url via fips registry
            dep_url = registry.get_url(fips_dir, dep)
            if not git.is_valid_url(dep_url) :
                log.error("'{}' cannot be resolved into a git url (in project '{}')".format(dep_url, proj_name))

            dep_proj_name = util.get_project_name_from_url(dep_url)
            if dep_proj_name not in result :
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                if project.is_valid_project_dir(dep_proj_dir) :
                    success, result = _rec_get_all_imports_exports(fips_dir, dep_proj_dir, dep_url, result)
                else :
                    success = False

                # break recursion on error
                if not success :
                    return success, result

    # done
    return success, result

#-------------------------------------------------------------------------------
def get_all_imports_exports(fips_dir, proj_dir) :
    """recursively get all imports/exports of a project, fails if any
    dependencies haven't been fetched yet, see _rec_get_imports_exports()
    for result dictionary structure

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :returns:           succes, and result dictionary object
    """
    result = OrderedDict()
    return _rec_get_all_imports_exports(fips_dir, proj_dir, None, result)

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
                    # directory already exists
                    log.info("dir '{}' exists".format(dep_proj_dir))
                    dep_ok = True

                # recuse
                if dep_ok :
                    handled = _rec_fetch_imports(fips_dir, dep_proj_dir, handled)

    # done, return the new handled array
    return handled

#-------------------------------------------------------------------------------
def fetch_imports(fips_dir, proj_dir) :
    """recursively git-clone the imports of a project, NOTE: existing
    repos will never be updated

    :param proj_dir:    existing project directory
    """
    _rec_fetch_imports(fips_dir, proj_dir, [])

