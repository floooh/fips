"""project-specific settings"""

import yaml
import os.path

from mod import log, util, config

valid_settings = ['config', 'target', 'jobs', 'ccache', 'iosteam', 'vscode-launch-configs']

default_settings = {
    'config':   config.get_default_config(),
    'target':   None,
    'jobs':     util.get_num_cpucores() + 2,
    'ccache':   False,
    'local':    False,
    'iosteam':  None,
    'vscode-launch-configs': 'all',
    'vscode-debug-type': 'cppdbg',
}

value_help = {
    'config':  'config-name',
    'target':  'target-name',
    'jobs':    'num-build-jobs',
    'ccache':  'on|off',
    'local':   'on|off',
    'iosteam': 'apple-team-id',
    'vscode-launch-configs': 'all|minimal|skip-build',
    'vscode-debug-type': 'default|lldb',
}

human_help = {
    'config':   'set active build config',
    'target':   'set active run target',
    'jobs':     'set number of parallel build jobs',
    'ccache':   'enable/disable using ccache',
    'local':    'place build files in project directory (useful for CI/CD)',
    'iosteam':  'Apple team id for iOS development',
    'vscode-launch-configs': 'set vscode debugger launch configs to generate',
    'vscode-debug-type': 'set vscode debugger type (lldb for CodeLLDB extension)',
}

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
    if key in default_settings:
        return default_settings[key]
    else:
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
        value_str = 'on' if value else 'off'
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

#-------------------------------------------------------------------------------
def get_all_settings(proj_dir):
    """return a dictionary with all setting key/value pairs

    :returns:   dictionary with all settings key/value pairs
    """
    util.ensure_valid_project_dir(proj_dir)
    settings = load(proj_dir)
    for key in default_settings:
        if key not in settings:
            settings[key] = default_settings[key]
    return settings
