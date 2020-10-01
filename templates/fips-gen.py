"""
    Code generator template file. This is called from a cmake
    code generator build target with the full path to a
    yaml file which contains detailed code gen params.
"""
import os
import sys
# FIXME PYTHON3
is_python3 = sys.version_info > (3,5)
if is_python3:
    import importlib.util
else:
    import imp

# template variable will be replaced with
# imported generator paths
gen_paths = [ $genpaths ]

# make imported generator modules visible to python module system
for path in gen_paths :
    sys.path.insert(0, path)

# yaml module is under the fips directory
import yaml
from mod import log
import genutil

def processFile(attrs) :
    # dynamically load (and execute) the generator module
    absPyPath = attrs['generator']
    input = attrs['in']
    out_src = attrs['out_src']
    out_hdr = attrs['out_hdr']
    if 'args' in attrs :
        args = attrs['args']
    else :
        args = None
    if 'env' in attrs :
        env = attrs['env']
    else :
        env = None
    genutil.setEnv(env)
    path, script = os.path.split(absPyPath)
    sys.path.insert(0, path)
    moduleName, ext = os.path.splitext(script)
    if is_python3:
        module = importlib.import_module(moduleName)
    else:
        # FIXME PYTHON2
        fp, pathname, description = imp.find_module(moduleName)
        module = imp.load_module(moduleName, fp, pathname, description)
    if args :
        module.generate(input, out_src, out_hdr, args)
    else :
        module.generate(input, out_src, out_hdr)

#=== entry point
if len(sys.argv) == 2 :
    with open(sys.argv[1], 'r') as f :
        items = yaml.load(f)
        for attrs in items :
            processFile(attrs)
else :
    print('Needs full path to a generator .yml file!')
    exit(10)
