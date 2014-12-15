"""project-specific settings"""

import yaml
import os.path
from mod import log, util, project, config

#-------------------------------------------------------------------------------
def get_default(key) :
    """get the default value for a settings key

    :param key:     settings key
    :returns:       default value, or None if key is invalid
    """
    if key == 'config' :
        return config.get_default_config()
    else :
        return None

#-------------------------------------------------------------------------------
def get(proj_dir, key) :
    """return settings value by key, default value if the value
    doesn't exist in the project-local settings file

    :param proj_dir:    absolute project directory
    :param key:         settings key
    :returns:           settings value, default value for key, or None
    """
    if not project.is_valid_project_dir(proj_dir) :
        log.error("not a valid project dir: '{}'".format(proj_dir))

    value = None
    path = proj_dir + '/.fips-settings.yml'
    if os.path.isfile(path) :
        f = open(path, 'r')
        settings = yaml.load(f)
        f.close()
        if key in settings :
            value = settings[key]

    if value is None :
        value = get_default(key)

    return value

#-------------------------------------------------------------------------------
def set(proj_dir, key, value) :
    """update a settings value by key and save project-local
    .fips-settings file

    :param proj_dir:    absolute project directory
    :param key:         settings key
    :param value:       new value associated with key
    """
    if not project.is_valid_project_dir(proj_dir) :
        log.error("not a valid project dir: '{}'".format(proj_dir))

    path = proj_dir + '/.fips-settings.yml'
    settings = {}

    # load existing settings file
    if os.path.isfile(path) :
        f = open(path, 'r')
        settings = yaml.load(f)
        f.close()

    # update value
    settings[key] = value

    # write back settings file
    f = open(path, 'w')
    yaml.dump(settings, f)
    f.close()

    proj_name = util.get_project_name_from_dir(proj_dir)
    log.info("'{}' set to '{}' in project '{}".format(key, value, proj_name))

#-------------------------------------------------------------------------------
def unset(proj_dir, key) :
    """delete a settings value from the project-local settings file

    :param proj_dir:    absolute project directory
    :param key:         settings key
    """
    if not project.is_valid_project_dir(proj_dir) :
        log.error("not a valid project dir: '{}'".format(proj_dir))

    path = proj_dir + '/.fips-settings.yml'
    settings = {}

    # load existing settings file
    if os.path.isfile(path) :
        f = open(path, 'r')
        settings = yaml.load(f)
        f.close()

    # clear key if exists
    if key in settings :
        del settings[key]

    # and save back
    f = open(path, 'w')
    yaml.dump(settings, f)
    f.close()

    proj_name = util.get_project_name_from_dir(proj_dir)
    log.info("'{}' unset in project '{}'".format(key, proj_name))

