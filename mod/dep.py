"""functions for external dependencies"""

import os
from collections import OrderedDict
from mod import log, util, registry, template
from mod.tools import git

#-------------------------------------------------------------------------------
def get_imports(proj_dir) :
    """get the imports from the fips.yml file in proj_dir

    :param proj_dir:    the project directory
    :returns:           dictionary object with imports (can be empty)
    """
    util.ensure_valid_project_dir(proj_dir)
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
    util.ensure_valid_project_dir(proj_dir)
    exports = {}
    dic = util.load_fips_yml(proj_dir)
    if 'exports' in dic :
        exports = dic['exports']
    if not 'header-dirs' in exports :
        exports['header-dirs'] = []
    if not 'lib-dirs' in exports :
        exports['lib-dirs'] = []
    if not 'defines' in exports :
        exports['defines'] = {}
    if not 'modules' in exports :
        exports['modules'] = {}
    return exports

#-------------------------------------------------------------------------------
def _rec_get_all_imports_exports(fips_dir, proj_dir, proj_url, result) :
    """recursively get all imported projects, their exported and
    imported modules in a dictionary object:
        
        project-1:
            url:    git-url (not valid for first, top-level project)
            exports:
                header-dirs: [ ]
                lib-dirs: [ ]
                defines: 
                    def-key: def-val
                    ...
                modules :
                    mod: dir
                    mod: dir
                ...
            imports:
                proj-name or url,
                proj-name or url,
                ...
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
            if not util.is_git_url(dep_url) :
                log.error("'{}' cannot be resolved into a git url (in project '{}')".format(dep_url, proj_name))

            dep_proj_name = util.get_project_name_from_url(dep_url)
            if dep_proj_name not in result :
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                if util.is_valid_project_dir(dep_proj_dir) :
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
            if not util.is_git_url(dep_url) :
                log.error("'{}' can't be resolved to a git url (in project '{}')".format(dep_url, proj_name))

            dep_proj_name = util.get_project_name_from_url(dep_url)
            if dep_proj_name not in handled:
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                log.colored(log.YELLOW, "=== dependency: '{}':".format(dep_proj_name))
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

#-------------------------------------------------------------------------------
def write_imports_files(fips_dir, proj_dir, dry_run=False) :
    """resolve imports of proj_dir and write a .fips-imports.cmake and
    .fips-gen.py file into the project directory

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param dry_run:     if true perform a dry run (used by 'fips diag')
    """

    ws_dir = util.get_workspace_dir(fips_dir)

    success, deps = get_all_imports_exports(fips_dir, proj_dir)
    if success :
        
        imported_modules = OrderedDict()
        imported_hdrdirs = []
        imported_libdirs = []
        imported_gendirs = []
        imported_defines = {}

        # for each project:
        for proj_name in deps :
           
            imports = deps[proj_name]['imports']
            exports = deps[proj_name]['exports']
            # for each imported project:
            for imp_proj in imports :
                
                # imp_proj can be a name or a url, we need the name
                imp_proj_name = imp_proj
                if util.is_git_url(imp_proj_name) :
                    imp_proj_name = util.get_project_name_from_url(imp_proj_name)

                # export of current import module
                dep_exports_mods = deps[imp_proj_name]['exports']['modules']
                dep_exports_hdrdirs = deps[imp_proj_name]['exports']['header-dirs']
                dep_exports_libdirs = deps[imp_proj_name]['exports']['lib-dirs']
                dep_exports_defines = deps[imp_proj_name]['exports']['defines']

                # add header search paths
                for imp_hdr in dep_exports_hdrdirs :
                    hdr_path = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_hdr)
                    if not os.path.isdir(hdr_path) :
                        log.warn("header search path '{}' not found in project '{}'".format(hdr_path, imp_proj_name))
                    if hdr_path not in imported_hdrdirs :
                        imported_hdrdirs.append(hdr_path)

                # add lib search paths
                for imp_lib in dep_exports_libdirs :
                    lib_path = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_lib)
                    if not os.path.isdir(lib_path) :
                        log.warn("lib search path '{}' not found in project '{}'".format(lib_path, imp_proj_name))
                    if lib_path not in imported_libdirs :
                        imported_libdirs.append(lib_path)

                # add defines
                for imp_def in dep_exports_defines :
                    if imp_def not in imported_defines :
                        imported_defines[imp_def] = dep_exports_defines[imp_def]
                    elif imported_defines[imp_def] != dep_exports_defines[imp_def] :
                        log.warn("define '{}={}' in '{}' collides with '{}={}' in earlier import".format(
                            imp_def, imported_defines[imp_def],
                            proj_name, 
                            imp_def, dep_exports_defines[imp_def]))

                # for each imported module:
                for imp_mod in dep_exports_mods :
                    imp_mod_src = dep_exports_mods[imp_mod]
                    # import module source directory (where module's CMakeLists.txt is)
                    src_dir = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_mod_src)
                    # cmake build subdirectory
                    build_dir = '{}_{}'.format(imp_proj_name, imp_mod)
                    if src_dir not in imported_modules :
                        imported_modules[src_dir] = build_dir

        if not dry_run :
            # write the .fips-imports.cmake file
            with open(proj_dir + '/.fips-imports.cmake', 'w') as f :
                f.write("#\n# generated by 'fips gen', don't edit, don't add to version control!\n#\n")
                for hdrdir in imported_hdrdirs :
                    f.write('include_directories("{}")\n'.format(hdrdir))
                for libdir in imported_libdirs :
                    f.write('link_directories("{}")\n'.format(libdir))
                for define in imported_defines :
                    value = imported_defines[define]
                    if type(value) is str :
                        f.write('add_definitions(-D{}="{}")\n'.format(define, value))
                    else :
                        f.write('add_definitions(-D{}={})\n'.format(define, value))
                for mod in imported_modules :
                    f.write('add_subdirectory("{}" "{}")\n'.format(mod, imported_modules[mod]))

            # write the .fips-imports.py file (copy from template)
            gen_search_paths = '"{}/generators",\n'.format(fips_dir)
            for imp_proj_name in deps :
                gen_dir = util.get_project_dir(fips_dir, imp_proj_name) + '/fips-generators'
                if os.path.isdir(gen_dir) :
                    gen_search_paths += '"' + gen_dir + '",\n' 
            template.copy_template_file(fips_dir, proj_dir, '.fips-gen.py', { 'genpaths': gen_search_paths}, True) 
    else :
        log.warn("imports are incomplete, please run 'fips fetch'")

#-------------------------------------------------------------------------------
def check_imports(fips_dir, proj_dir) :
    """do various checks on the imports of a project

    :param fips_dir: absolute fips directory
    :param proj_dir: absolute project directory
    :returns:   True if checks were valid
    """

    # check whether any imported projects are in sync with the remote git repo
    success, imported_projects = get_all_imports_exports(fips_dir, proj_dir)
    num_imports = 0
    for imp_proj_name in imported_projects :
        imp_proj_dir = util.get_project_dir(fips_dir, imp_proj_name)

        # don't git-check the top-level project directory
        if imp_proj_dir != proj_dir :
            num_imports += 1
            log.info("git status of '{}':".format(imp_proj_name))
            if os.path.isdir(imp_proj_dir) :
                if git.check_out_of_sync(imp_proj_dir) :
                    log.warn("  '{}' is out of sync with remote git repo".format(imp_proj_dir))
                else :
                    log.colored(log.GREEN, '  ok')
            else :
                log.warn("  '{}' does not exist, please run 'fips fetch'".format(imp_proj_dir))
    if success and num_imports == 0 :
        log.info('  none')

    # run write_imports_file as dry run
    write_imports_files(fips_dir, proj_dir, True)

