"""
    Code generator template file. This is called from a cmake
    code generator build target with the full path to a 
    yaml file which contains detailed code gen params.
"""
import sys
import os
import imp

# template variable will be replaced with 
# imported generator paths
gen_paths = [ $genpaths ]

# make imported generator modules visible to python module system
for path in gen_paths :
    sys.path.insert(0, path)

# yaml module is under the fips directory
import yaml

def processFile(absPyPath, inputs, outputs) :
    # dynamically load (and execute) the generator module
    path, script = os.path.split(absPyPath)
    moduleName, ext = os.path.splitext(script)
    fp, pathname, description = imp.find_module(moduleName, [path])
    module = imp.load_module(moduleName, fp, pathname, description)
    module.generate(absPyPath, inputs, outputs)

#=== entry point
if len(sys.argv) == 2 :
    with open(sys.argv[1], 'r') as f :
        items = yaml.load(f)
        for attrs in items :
            if attrs['type'] == 'simple' :
                processFile(attrs['script'], [attrs['script']], attrs['outputs'])
            else :
                print("NOT IMPLEMENTED YET")
else :
    print('Needs full path to a generator .yml file!')
    exit(10)
