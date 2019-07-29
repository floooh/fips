"""functions for external dependencies"""

import os
import filecmp

from collections import OrderedDict
from mod import log, util, registry, template
from mod.tools import git

#-------------------------------------------------------------------------------
def get_imports(fips_dir, proj_dir) :
    """get the imports from the fips.yml file in proj_dir

    :param proj_dir:    the project directory
    :returns:           dictionary object with imports (can be empty)
    """
    proj_name = util.get_project_name_from_dir(proj_dir)
    imports = {}
    if util.is_valid_project_dir(proj_dir) :
        dic = util.load_fips_yml(proj_dir)
        if 'imports' in dic :
            imports = dic['imports']

        # warn if this is an old-style list instead of new style dict
        if imports :
            if type(imports) is list :
                log.warn("imports in '{}/fips.yml' uses obsolete array format".format(proj_dir))
                
                # convert old style to new dict format
                # FIXME: should be removed after a while
                new_imports = {}
                for dep in imports :
                    dep_url = registry.get_url(fips_dir, dep)
                    if not util.is_git_url(dep_url) :
                        log.error("'{}' cannot be resolved into a git url (in project '{}')".format(dep_url, proj_name))
                    dep_proj_name = util.get_project_name_from_url(dep_url)
                    new_imports[dep_proj_name] = {}
                    new_imports[dep_proj_name]['git']    = util.get_giturl_from_url(dep_url)
                    new_imports[dep_proj_name]['branch'] = util.get_gitbranch_from_url(dep_url)
                imports = new_imports
            elif type(imports) is dict :
                for dep in imports :
                    if not 'branch' in imports[dep] :
                        imports[dep]['branch'] = 'master'
                    if not 'cond' in imports[dep] :
                        imports[dep]['cond'] = None
                    if not 'git' in imports[dep] :
                        log.error("no git URL in import '{}' in '{}/fips.yml'!\n".format(dep, proj_dir))
                    if not 'group' in imports[dep] :
                        imports[dep]['group'] = None
            else :
                log.error("imports in '{}/fips.yml' must be a dictionary!".format(proj_dir))
    return imports

#-------------------------------------------------------------------------------
def get_exports(proj_dir) :
    """get the exports from the fips.yml file in proj_dir

    :param proj_dir:    the project directory
    :returns:           dictionary object with exports (can be empty)
    """
    exports = {}
    if util.is_valid_project_dir(proj_dir) :
        dic = util.load_fips_yml(proj_dir)
        if 'exports' in dic :
            exports = dic['exports']
    if not 'header-dirs' in exports :
        exports['header-dirs'] = []
    if not 'conditional-header-dirs' in exports :
        exports['conditional-header-dirs'] = []
    if not 'lib-dirs' in exports :
        exports['lib-dirs'] = []
    if not 'defines' in exports :
        exports['defines'] = {}
    if not 'modules' in exports :
        exports['modules'] = {}
    return exports

#-------------------------------------------------------------------------------
def get_policy(proj_dir, policy) :
    """checks whether a policy is defined in the projects fips.yml
    and returns its bool value, or the default if not defined.

    :param proj_dir:    the project directory
    :param policy:      the policy string name
    :returns:           true/false
    """
    def_policies = {
        'no_auto_import': False
    }
    if util.is_valid_project_dir(proj_dir) :
        dic = util.load_fips_yml(proj_dir)
        if 'policies' in dic and type(dic['policies']) is dict:
            if policy in dic['policies'] :
                return dic['policies'][policy]
    # not found, return default
    if policy in def_policies :
        return def_policies[policy]
    else :
        # unknown policy, return None
        log.error("unknown policy name: '{}'".format(policy))
        return None

#-------------------------------------------------------------------------------
def _rec_get_all_imports_exports(fips_dir, proj_dir, result) :
    """recursively get all imported projects, their exported and
    imported modules in a dictionary object:
        
        project-1:
            url:    git-url (not valid for first, top-level project)
            exports:
                header-dirs: [ ]
                conditional-header-dirs:
                    dir: cmake-if condition string
                lib-dirs: [ ]
                defines: 
                    def-key: def-val
                    ...
                modules :
                    mod: dir
                    mod: dir
                ...
            imports:
                name:
                    git:    [git-url]
                    branch: [optional: branch or tag]
                    cond:   [optional: cmake-if condition string conditionally including the dependency]
                name:
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
        imports = get_imports(fips_dir, proj_dir)
        exports = get_exports(proj_dir)
        for dep_proj_name in imports :
            if dep_proj_name not in result :
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                dep_url = imports[dep_proj_name]['git']
                success, result = _rec_get_all_imports_exports(fips_dir, dep_proj_dir, result)
                # break recursion on error
                if not success :
                    return success, result

        result[proj_name] = {}
        result[proj_name]['proj_dir'] = proj_dir
        result[proj_name]['imports'] = imports 
        result[proj_name]['exports'] = exports 

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
    return _rec_get_all_imports_exports(fips_dir, proj_dir, result)

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

        imports = get_imports(fips_dir, proj_dir)
        for dep in imports:
            dep_proj_name = dep
            if dep not in handled:
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                log.colored(log.YELLOW, "=== dependency: '{}':".format(dep_proj_name))
                dep_ok = False
                if not os.path.isdir(dep_proj_dir) :
                    # directory did not exist, do a fresh git clone
                    dep = imports[dep_proj_name]
                    git_commit = None if 'rev' not in dep else dep['rev']
                    if git_commit :
                        if 'depth' in dep :
                            # when using rev, we may not want depth because the revision may not be reachable
                            log.colored(log.YELLOW, "=== 'depth' was ignored because parameter 'rev' is specified.")
                        dep['depth'] = None
                    git_depth = git.clone_depth if not git_commit and 'depth' not in dep else dep['depth']
                    git_url = dep['git']
                    git_branch = dep['branch']
                    if git.clone(git_url, git_branch, git_depth, dep_proj_name, ws_dir) :
                        if git_commit :
                            log.colored(log.YELLOW, "=== revision: '{}':".format(git_commit))
                            dep_ok = git.checkout(dep_proj_dir, git_commit)
                        else :
                            dep_ok = True
                    else :
                        log.error('failed to git clone {} into {}'.format(git_url, dep_proj_dir))
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
def gather_imports(fips_dir, proj_dir) :
    """resolve imports of proj_dir and returns a big dictionary
    with all imported data, which can then be written with write_imports()

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param dry_run:     if true perform a dry run (used by 'fips diag')
    :returns:           a big dictionary which can be written with write_imports()
                        or None on error
    """
    imported = OrderedDict()
    ws_dir = util.get_workspace_dir(fips_dir)
    success, deps = get_all_imports_exports(fips_dir, proj_dir)

    unique_defines = {}
    unique_modules = {}
    
    if success :
        
        # for each project:
        for proj_name in deps :

            imports = deps[proj_name]['imports']
            exports = deps[proj_name]['exports']
            # for each imported project:
            for imp_proj_name in sorted(imports) :
                
                imported[imp_proj_name] = {}
                imported[imp_proj_name]['modules'] = OrderedDict()
                imported[imp_proj_name]['hdrdirs'] = []
                imported[imp_proj_name]['condhdrdirs'] = {}
                imported[imp_proj_name]['libdirs'] = []
                imported[imp_proj_name]['defines'] = {}
                imported[imp_proj_name]['cond'] = imports[imp_proj_name]['cond']
                imported[imp_proj_name]['group'] = imports[imp_proj_name]['group']

                # add header search paths
                for imp_hdr in deps[imp_proj_name]['exports']['header-dirs'] :
                    hdr_path = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_hdr)
                    hdr_path = os.path.normpath(hdr_path).replace('\\', '/')
                    if not os.path.isdir(hdr_path) :
                        log.warn("header search path '{}' not found in project '{}'".format(hdr_path, imp_proj_name))
                    imported[imp_proj_name]['hdrdirs'].append(hdr_path)

                # add conditional header search paths
                for imp_hdr in deps[imp_proj_name]['exports']['conditional-header-dirs'] :
                    if not 'path' in imp_hdr :
                        log.warn("no 'path' key in conditional-header-dirs in project {}".format(imp_proj_name))
                    elif not 'cond' in imp_hdr :
                        log.warn("no 'cond' key in conditional-header-dirs in project {}".format(imp_proj_name))
                    else :
                        hdr_path = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_hdr['path'])
                        hdr_path = os.path.normpath(hdr_path).replace('\\', '/')
                        if not os.path.isdir(hdr_path) :
                            log.warn("conditional header search path '{}' not found in project '{}'".format(hdr_path, imp_proj_name))
                        value = imp_hdr['cond']
                        imported[imp_proj_name]['condhdrdirs'][hdr_path] = value

                # add lib search paths
                for imp_lib in deps[imp_proj_name]['exports']['lib-dirs'] :
                    lib_path = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_lib)
                    lib_path = os.path.normpath(lib_path).replace('\\', '/')
                    if not os.path.isdir(lib_path) :
                        log.warn("lib search path '{}' not found in project '{}'".format(lib_path, imp_proj_name))
                    imported[imp_proj_name]['libdirs'].append(lib_path)

                # add defines
                for imp_def in deps[imp_proj_name]['exports']['defines'] :
                    # hmm, no check whether this define collides with an earlier define...
                    value = deps[imp_proj_name]['exports']['defines'][imp_def]
                    imported[imp_proj_name]['defines'][imp_def] = value
                    if imp_def in unique_defines :
                        if unique_defines[imp_def] != value :
                            log.warn("C define collision: '{}={}' in '{}' collides with '{}={}' in earlier import".format(
                                imp_def, value, imp_proj_name, imp_def, unique_defines[define]))
                        unique_defines[imp_def] = value

                # for each imported module:
                for imp_mod in deps[imp_proj_name]['exports']['modules'] :
                    imp_mod_src = deps[imp_proj_name]['exports']['modules'][imp_mod]
                    # import module source directory (where module's CMakeLists.txt is)
                    src_dir = '{}/{}/{}'.format(ws_dir, imp_proj_name, imp_mod_src)
                    # cmake build subdirectory
                    build_dir = '{}_{}'.format(imp_proj_name, imp_mod)
                    imported[imp_proj_name]['modules'][src_dir] = build_dir
                    if imp_mod in unique_modules :
                        if unique_modules[imp_mod] != src_dir :
                            log.warn("Import module '{}=>{}' in '{}' collides with '{}=>{}' in earlier import".format(
                                imp_mod, src_dir, imp_proj_name, imp_mod, unique_modules[imp_mod]))
                        unique_modules[imp_mod] = src_dir
        return imported

    else :
        log.warn("imports are incomplete, please run 'fips fetch'")
        return None

#-------------------------------------------------------------------------------
def write_imports(fips_dir, proj_dir, cfg_name, imported) :
    """write the big imports map created with 'gather_imports'
    to a .fips-imports.cmake file in the current project

    :params fips_dir:   absolute path to fips
    :params proj_dir:   absolute path to current project
    :params imported:   the imports dictionary created with 'gather_imports'
    """

    if imported is not None:
        unique_hdrdirs = []
        unique_condhdrdirs = {}
        unique_libdirs = []
        unique_defines = {}
        unique_modules = {}

        # write a temporary .fips-imports.cmake.tmp file,
        # this will replace the old file, but only if the
        # content is different, this will prevent an unnecessary
        # cmake run if the imports haven't changed
        import_filename = proj_dir + '/.fips-imports.cmake'
        import_tmp_filename = import_filename + '.tmp'
        with open(import_tmp_filename, 'w') as f :
            f.write("#\n# generated by 'fips gen', don't edit, don't add to version control!\n#\n")
            
            for imp_proj_name in imported :
                imp_proj_dir = util.get_project_dir(fips_dir, imp_proj_name)
                
                if imported[imp_proj_name]['cond']:
                    f.write('if ({})\n'.format(imported[imp_proj_name]['cond']))

                # add include and lib search paths
                if imp_proj_dir != proj_dir :
                    f.write('if (EXISTS "{}/fips-include.cmake")\n'.format(imp_proj_dir))
                    f.write('    include("{}/fips-include.cmake")\n'.format(imp_proj_dir))
                    f.write('elseif (EXISTS "{}/fips-files/include.cmake")\n'.format(imp_proj_dir))
                    f.write('    include ("{}/fips-files/include.cmake")\n'.format(imp_proj_dir))
                    f.write('endif()\n')
                    f.write('if (EXISTS "{}/lib/${{FIPS_PLATFORM_NAME}}")\n'.format(imp_proj_dir))
                    f.write('    link_directories("{}/lib/${{FIPS_PLATFORM_NAME}}")\n'.format(imp_proj_dir))
                    f.write('endif()\n')

                # add header search paths
                for hdrdir in imported[imp_proj_name]['hdrdirs'] :
                    if hdrdir not in unique_hdrdirs :
                        f.write('include_directories("{}")\n'.format(hdrdir))
                        unique_hdrdirs.append(hdrdir)

                # add conditional header search paths
                for hdrdir in imported[imp_proj_name]['condhdrdirs'] :
                    value = imported[imp_proj_name]['condhdrdirs'][hdrdir]
                    if hdrdir not in unique_condhdrdirs :
                        unique_condhdrdirs[hdrdir] = value
                        f.write('if ({})\n'.format(value))
                        f.write('    include_directories("{}")\n'.format(hdrdir))
                        f.write('endif()\n')

                # add lib search paths
                for libdir in imported[imp_proj_name]['libdirs'] :
                    if libdir not in unique_libdirs :
                        f.write('link_directories("{}")\n'.format(libdir))
                        unique_libdirs.append(libdir)

                # add defines
                for define in imported[imp_proj_name]['defines'] :
                    value = imported[imp_proj_name]['defines'][define]
                    if define not in unique_defines :
                        unique_defines[define] = value
                        if type(value) is str :
                            f.write('add_definitions(-D{}="{}")\n'.format(define, value))
                        else :
                            f.write('add_definitions(-D{}={})\n'.format(define, value))

                # add import modules
                if len(imported[imp_proj_name]['modules']) > 0 :
                    import_functions = []

                    # first add all module import functions
                    for module in imported[imp_proj_name]['modules'] :
                        module_path = imported[imp_proj_name]['modules'][module]
                        if module not in unique_modules :
                            unique_modules[module] = module_path
                            import_func = 'fips_import_{}'.format(module_path).replace('-','_')
                            import_functions.append(import_func)
                            f.write('macro({})\n'.format(import_func))
                            f.write('    set(FIPS_IMPORT 1)\n')
                            f.write('    add_subdirectory("{}" "{}")\n'.format(module, module_path))
                            f.write('    set(FIPS_IMPORT)\n')
                            f.write('endmacro()\n')

                    # if auto-import is enabled, also actually import all modules
                    f.write('if (FIPS_AUTO_IMPORT)\n')
                    group = "Imports"
                    if imported[imp_proj_name]['group'] :
                        group += "/" + imported[imp_proj_name]['group']                        
                    if len(imported[imp_proj_name]['modules']) > 3 :
                        group += "/" + imp_proj_name
                    f.write('    fips_ide_group("{}")\n'.format(group))
                    for import_func in import_functions :
                        f.write('    {}()\n'.format(import_func))
                    f.write('    fips_ide_group("")\n')
                    f.write('endif()\n')
                
                if imported[imp_proj_name]['cond']:
                    f.write('endif()\n')

        # check content of old and new file, only replace if changed
        imports_dirty = True
        if os.path.isfile(import_filename) :
            if filecmp.cmp(import_filename, import_tmp_filename, shallow=False) :
                imports_dirty = False
        if imports_dirty :
            if os.path.isfile(import_filename) :
                os.remove(import_filename)
            os.rename(import_tmp_filename, import_filename)
        else :
            os.remove(import_tmp_filename)

    # write the .fips-imports.py file (copy from template)
    gen_search_paths  = '"{}","{}/generators",\n'.format(fips_dir, fips_dir)
    proj_gen_dir = util.get_generators_dir(proj_dir)
    if proj_gen_dir:
        gen_search_paths += '"{}","{}",\n'.format(proj_dir, proj_gen_dir)
    for imp_proj_name in imported :
        gen_dir = util.get_generators_dir(util.get_project_dir(fips_dir, imp_proj_name))
        if gen_dir:
            gen_search_paths += '"' + gen_dir + '",\n' 
    proj_name = util.get_project_name_from_dir(proj_dir)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg_name); 
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    template.copy_template_file(fips_dir, build_dir, 'fips-gen.py', { 'genpaths': gen_search_paths}, True)

#-------------------------------------------------------------------------------
def gather_and_write_imports(fips_dir, proj_dir, cfg_name) :
    """first does and gather_imports, then a write_imports with the result"""
    imports = gather_imports(fips_dir, proj_dir)
    if imports is not None :
        write_imports(fips_dir, proj_dir, cfg_name, imports)
    else :
        log.error("project imports are incomplete, please run 'fips fetch'")

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
        imp_proj_dir = imported_projects[imp_proj_name]['proj_dir']

        # don't git-check the top-level project directory
        if imp_proj_dir != proj_dir :
            num_imports += 1
            log.info("git status of '{}':".format(imp_proj_name))
            if os.path.isdir(imp_proj_dir) :
                if os.path.isdir("{}/.git".format(imp_proj_dir)) :
                    if git.check_out_of_sync(imp_proj_dir) :
                        log.warn("  '{}' is out of sync with remote git repo".format(imp_proj_dir))
                    else :
                        log.colored(log.GREEN, '  uptodate')
                else :
                    log.colored(log.GREEN, "  '{}' is not a git repository".format(imp_proj_dir))
            else :
                log.warn("  '{}' does not exist, please run 'fips fetch'".format(imp_proj_dir))
    if success and num_imports == 0 :
        log.info('  none')

    # gather imports, this will dump warnings
    gather_imports(fips_dir, proj_dir)

#-------------------------------------------------------------------------------
def check_local_changes(fips_dir, proj_dir) :
    """this is a variation of check_imports which just checks for local
    (uncommitted or unpushed) changes.

    :param fips_dir: absolute fips directory
    :param proj_dir: absolute project directory
    :returns:   True if checks were valid
    """
    success, imported_projects = get_all_imports_exports(fips_dir, proj_dir)
    num_imports = 0
    for imp_proj_name in imported_projects :
        imp_proj_dir = imported_projects[imp_proj_name]['proj_dir']

        # don't git-check the top-level project directory
        if imp_proj_dir != proj_dir :
            num_imports += 1
            log.info("checking '{}':".format(imp_proj_name))
            if os.path.isdir(imp_proj_dir) :
                if git.has_local_changes(imp_proj_dir) :
                    log.warn("  '{}' has local changes (uncommitted and/or unpushed)".format(imp_proj_dir))
                else :
                    log.colored(log.GREEN, '  no local changes')
            else :
                log.warn("  '{}' does not exist, please run 'fips fetch'".format(imp_proj_dir))
    if success and num_imports == 0 :
        log.info('  none')

#-------------------------------------------------------------------------------
def _rec_update_imports(fips_dir, proj_dir, handled) :
    """same as _rec_fetch_imports() but for updating the imported projects
    """
    ws_dir = util.get_workspace_dir(fips_dir)
    proj_name = util.get_project_name_from_dir(proj_dir)
    if proj_name not in handled :
        handled.append(proj_name)
        imports = get_imports(fips_dir, proj_dir)
        for dep in imports:
            dep_proj_name = dep
            if dep not in handled:
                dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
                log.colored(log.YELLOW, "=== dependency: '{}':".format(dep_proj_name))
                dep_ok = False
                if os.path.isdir(dep_proj_dir) :
                    if os.path.isdir("{}/.git".format(dep_proj_dir)) :
                        dep = imports[dep_proj_name]
                        git_commit = None if 'rev' not in dep else dep['rev']
                        if git.has_local_changes(dep_proj_dir) :
                            log.warn("  '{}' has local changes, skipping...".format(dep_proj_dir))
                        else :
                            log.colored(log.BLUE, "  updating '{}'...".format(dep_proj_dir))
                            git.update(dep_proj_dir)
                            if git_commit:
                                log.colored(log.YELLOW, "=== revision: '{}':".format(git_commit))
                                dep_ok = git.checkout(dep_proj_dir, git_commit)
                            else:
                                dep_ok = True
                    else :
                        log.colored(log.BLUE, "  '{}' is not a git repository".format(dep_proj_dir))
                else :
                    log.warn("  '{}' does not exist, please run 'fips fetch'".format(dep_proj_dir))
                # recuse
                if dep_ok :
                    handled = _rec_update_imports(fips_dir, dep_proj_dir, handled)
    # done, return the new handled array
    return handled

#-------------------------------------------------------------------------------
def update_imports(fips_dir, proj_dir):
    """runs git.update on each import (only if the import has no local changes)

    :param fips_dir: absolute fips directory
    :param proj_dir: absolute project directory
    :returns:   True if checks were valid
    """
    _rec_update_imports(fips_dir, proj_dir, [])
