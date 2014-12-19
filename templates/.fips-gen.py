"""code generator template file"""

import sys
import os
import imp

# template variable will be replaced with 
# imported generator paths
gen_paths = [ $genpaths ]

# make imported generator modules visible to python module system
for path in gen_paths :
    sys.path.insert(0, path)

def processFile(absPyPath) :
    # dynamically load (and execute) the generator module
    path, script = os.path.split(absPyPath)
    moduleName, ext = os.path.splitext(script)
    fp, pathname, description = imp.find_module(moduleName, [path])
    module = imp.load_module(moduleName, fp, pathname, description)
    module.generate(path + '/', moduleName)

#=== entry point
if len(sys.argv) > 1 :
    for arg in sys.argv[1:] :
        print '## processing: {}'.format(arg)
        processFile(arg)
else :
    print 'Needs full path to a generator py file!'

