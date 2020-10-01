"""access to verb modules (local and imported"""

import sys
# FIXME PYTHON2
is_python3 = sys.version_info > (3,5)
import os
import glob
if is_python3:
    import importlib.util
else:
    import imp
from collections import OrderedDict

from mod import log, util, dep

# dictionary of "name: module"
verbs = {}

# dictionary of "projname: name"
proj_verbs = OrderedDict()

#-------------------------------------------------------------------------------
def import_verbs_from(proj_name, proj_dir, verb_dir) :
    """import all verb modules from a directory, populates the
    verb and proj_verbs global variables

    :param proj_dir:    name of project that owns verb_dir
    :param verb_dir:    directory with verb python scripts (can be None)
    """
    global verbs, proj_verbs

    # make sure project-verbs find their modules
    sys.path.insert(0, proj_dir)

    if verb_dir and os.path.isdir(verb_dir):
        # get all .py file in verb dir
        verb_paths = glob.glob(verb_dir + '/*.py')
        if verb_paths :
            for verb_path in verb_paths :
                verb_module_name = os.path.split(verb_path)[1]
                verb_module_name = os.path.splitext(verb_module_name)[0]
                if not verb_module_name.startswith('__') :
                    if is_python3:
                        spec = importlib.util.spec_from_file_location(verb_module_name, verb_path)
                        verb_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(verb_module)
                    else:
                        # FIXME: PYTHON2
                        fp, pathname, desc = imp.find_module(verb_module_name, [verb_dir])
                        verb_module = imp.load_module(verb_module_name, fp, pathname, desc)
                    verbs[verb_module_name] = verb_module
                    if proj_name not in proj_verbs :
                        proj_verbs[proj_name] = []
                    proj_verbs[proj_name].append(verb_module_name)

#-------------------------------------------------------------------------------
def import_verbs(fips_dir, proj_dir) :
    """import verbs from local and imported projects, populates
    the 'verbs' and 'proj_verbs' dictionaries

    :param fipsdir:     absolute fips directory
    :param proj_dir:    absolute project directory
    """

    # first import verbs from fips directory
    import_verbs_from('fips', fips_dir, fips_dir + '/verbs')

    # now go through all imported projects
    if fips_dir != proj_dir :
        _, imported_projs = dep.get_all_imports_exports(fips_dir, proj_dir)
        for imported_proj_name in imported_projs :
            imported_proj_dir = imported_projs[imported_proj_name]['proj_dir']
            import_verbs_from(imported_proj_name, imported_proj_dir, util.get_verbs_dir(imported_proj_dir))



