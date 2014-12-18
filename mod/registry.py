"""implement the fips project registry"""

import yaml

registry = None

#-------------------------------------------------------------------------------
def load(fips_dir) :
    """load registry on demand"""
    global registry
    if registry is None :
        with open(fips_dir + '/registry.yml', 'r') as f :
            registry = yaml.load(f)

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

#-------------------------------------------------------------------------------
def get_url(fips_dir, name_or_url) :
    """Checks if name_or_url is in the registry, if yes, return url
    from registry, otherwise return name_or_url. This is useful
    if a parameter can be either a project name or a valid URL, and
    must be converted into an URL.

    :param fips_dir:    the absolute fips directory
    :param name_or_url: a project-name or URL
    :returns:           URL from registry, or the original name_or_url param
    """
    load(fips_dir)
    if name_or_url in registry :
        return registry[name_or_url]
    else :
        return name_or_url
