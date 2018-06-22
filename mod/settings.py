"""project-specific settings"""

import yaml
import os.path

from mod import log, util, config

#-------------------------------------------------------------------------------
def load(proj_dir) :
    """load the .fips-settings.yml file from project directory

    :param proj_dir:    absolute project directory
    :returns:           dictionary object
    """
    settings = None
    path = proj_dir + '/.fips-settings.yml'
    if os.path.isfile(path) :
        with open(path, 'r') as f :
            settings = yaml.load(f)
    if not settings :
        settings = {}
    return settings

#-------------------------------------------------------------------------------
def save(proj_dir, settings) :
    """save settings back to .fips-settings.yml file in project directory

    :param proj_dir:    absolute project directory
    :param settings:    settings dictionary object
    """
    path = proj_dir + '/.fips-settings.yml'
    with open(path, 'w') as f :
        yaml.dump(settings, f)
    
#-------------------------------------------------------------------------------
def get_default(key) :
    """get the default value for a settings key

    :param key:     settings key
    :returns:       default value, or None if key is invalid
    """
    if key == 'config' :
        return config.get_default_config()
    elif key == 'target' :
        return None
    elif key == 'jobs' :
        # this is what ninja seems to do for default num jobs
        return util.get_num_cpucores() + 2
    elif key == 'ccache' :
        return False
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
    util.ensure_valid_project_dir(proj_dir)

    value = None
    settings = load(proj_dir)
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
    util.ensure_valid_project_dir(proj_dir)

    settings = load(proj_dir)
    settings[key] = value
    save(proj_dir, settings)

    proj_name = util.get_project_name_from_dir(proj_dir)
    if type(value) is bool :
        value_str = 'on' if value else 'off';
    else :
        value_str = str(value)
    log.info("'{}' set to '{}' in project '{}'".format(key, value_str, proj_name))

#-------------------------------------------------------------------------------
def unset(proj_dir, key) :
    """delete a settings value from the project-local settings file

    :param proj_dir:    absolute project directory
    :param key:         settings key
    """
    util.ensure_valid_project_dir(proj_dir)

    settings = load(proj_dir)
    if key in settings :
        del settings[key]
    save(proj_dir, settings)

    proj_name = util.get_project_name_from_dir(proj_dir)
    log.info("'{}' unset in project '{}'".format(key, proj_name))

