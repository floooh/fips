"""implement the fips project registry"""

import yaml

registry = None

#-------------------------------------------------------------------------------
def load(fips_dir) :
    """load registry on demand"""
    global registry
    if registry is None :
        f = open(fips_dir + '/registry.yml', 'r')
        registry = yaml.load(f)
        f.close()

#-------------------------------------------------------------------------------
def exists(fips_dir, proj_name) :
    """check if a project exists in the registry

    :param fips_dir:    absolute path to fips
    :param proj_name:   short-name of project
    :returns:           True if project is in the registry
    """
    load(fips_dir)
    return proj_name in registry

#-------------------------------------------------------------------------------
def lookup_url(fips_dir, proj_name) :
    """lookup git url for project name, return None if not found

    :param fips_dir:    absolute path to fips
    :param proj_name:   project name
    :returns:           git url from registry, or None
    """
    load(fips_dir)
    if proj_name in registry :
        return registry[proj_name]
    else :
        return None

