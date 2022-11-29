'''VSCode helper functions'''
import platform,subprocess, os, json, inspect, shutil, copy
from mod import util, log, verb, dep
from mod.tools import cmake

name = 'vscode'
platforms = ['osx','linux','win']
optional = True
not_found = 'used as IDE with vscode configs'

#------------------------------------------------------------------------------
def try_exists(exe_name):
    try:
        if platform.system() == 'Windows':
            subprocess.check_output('{} --version'.format(exe_name), shell=True)
        else:
            subprocess.check_output([exe_name, '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#------------------------------------------------------------------------------
def exe_name():
    if try_exists('code'):
        return 'code'
    else:
        # open source version on RaspberryPi
        return 'code-oss'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if 'code' is in the path
    :returns:   True if code is in the path
    """
    if exe_name() != 'code':
        return try_exists('code-oss')
    else:
        return True

#------------------------------------------------------------------------------
def match(build_tool):
    return build_tool in ['vscode_cmake', 'vscode_ninja']

#------------------------------------------------------------------------------
def run(proj_dir):
    exe = exe_name()
    proj_name = util.get_project_name_from_dir(proj_dir)
    try:
        subprocess.call('{} .vscode/{}.code-workspace'.format(exe, proj_name), cwd=proj_dir, shell=True)
    except OSError:
        log.error("Failed to run Visual Studio Code as '{}'".format(exe))

#-------------------------------------------------------------------------------
def write_launch_json(fips_dir, proj_dir, vscode_dir, cfg, proj_settings):
    '''write the .vscode/launch.json file'''
    launch = {
        'version': '0.2.0',
        'configurations': []
    }
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
    launch_config = {
        'request': 'launch',
        'program': '${command:cmake.launchTargetPath}',
        'cwd': deploy_dir,
        'stopAtEntry': False,
        'args': [],

    }
    host_platform = util.get_host_platform()
    if host_platform == 'win':
        launch_config['type'] = 'cppvsdbg'
    elif host_platform == 'linux':
        launch_config['type'] = 'cppdbg'
        launch_config['MIMode'] = 'gdb'
    else:
        launch_config['type'] = 'cppdbg'
        launch_config['MIMode'] = 'lldb'

    launch_config['name'] = 'Debug Current Target'
    launch['configurations'].append(copy.deepcopy(launch_config))

    launch_config['name'] = 'Debug Current Target (Stop at Entry)'
    launch_config['stopAtEntry'] = True
    launch['configurations'].append(copy.deepcopy(launch_config))

    # add a python code-generator debug config
    #
    #   FIXME: this no longer works (e.g. pythonPath is not recognized)
    #
    #proj_name = util.get_project_name_from_dir(proj_dir)
    #build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    #c = {
    #    'name': 'fips codegen',
    #    'type': 'python',
    #    'request': 'launch',
    #    'stopOnEntry': True,
    #    'pythonPath': '${config:python.pythonPath}',
    #    'program': build_dir + '/fips-gen.py',
    #    'args': [ build_dir + '/fips_codegen.yml' ],
    #    "cwd": proj_dir,
    #    "debugOptions": [
    #        "WaitOnAbnormalExit",
    #        "WaitOnNormalExit",
    #        "RedirectOutput"
    #    ]
    #}
    #launch['configurations'].append(c)

    # add a python debug config for each fips verb
    #
    #   FIXME: this no longer works (e.g. pythonPath is not recognized)
    #
    # for verb_name, verb_mod in verb.verbs.items() :
    #     # ignore standard verbs
    #     if fips_dir not in inspect.getfile(verb_mod):
    #         c = {
    #             'name': 'fips {}'.format(verb_name),
    #             'type': 'python',
    #             'request': 'launch',
    #             'stopOnEntry': True,
    #             'pythonPath': '${config:python.pythonPath}',
    #             'program': proj_dir + '/fips',
    #             'args': [ verb_name ],
    #             'cwd': proj_dir,
    #             "debugOptions": [
    #                 "WaitOnAbnormalExit",
    #                 "WaitOnNormalExit",
    #                 "RedirectOutput"
    #             ]
    #         }
    #         launch['configurations'].append(c)

    launch_path = vscode_dir + '/launch.json'
    log.info('  writing {}'.format(launch_path))
    with open(launch_path, 'w') as f:
        json.dump(launch, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def write_code_workspace_file(fips_dir, proj_dir, impex, cfg):
    '''write a multiroot-workspace config file'''
    vscode_dir = proj_dir + '/.vscode'
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
    ws = {
        'folders': [],
        'settings': {
            'cmake.statusbar.advanced': {
                'ctest': { 'visibility': 'hidden' },
                'testPreset': { 'visibility': 'hidden' },
                'debug': { 'visibility': 'hidden' },
                'workspace': { 'visibility': 'hidden' }
            },
            'cmake.debugConfig': { 'cwd': deploy_dir },
            'cmake.autoSelectActiveFolder': False,
            'cmake.ignoreCMakeListsMissing': True,
            'cmake.configureOnOpen': False,
        }
    }
    # add dependencies in reverse order, so that main project is first
    for dep_proj_name in reversed(impex):
        dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
        excluded = False
        if 'vscode_exclude_from_workspace' in cfg:
            for exclude_dep in cfg['vscode_exclude_from_workspace']:
                if dep_proj_name == exclude_dep:
                    excluded = True
                    break
        if not excluded:
            ws['folders'].append({ 'path': dep_proj_dir })
    proj_name = util.get_project_name_from_dir(proj_dir)
    ws_path = '{}/{}.code-workspace'.format(vscode_dir, proj_name)
    log.info('  writing {}'.format(ws_path))
    with open(ws_path, 'w') as f:
        json.dump(ws, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def remove_vscode_tasks_launch_files(fips_dir, proj_dir, impex, cfg):
    '''walks through the dependencies, and deletes the .vscode/tasks.json
    and .vscode/launch.json files
    '''
    for dep_proj_name in reversed(impex):
        dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
        tasks_path = dep_proj_dir + '/.vscode/tasks.json'
        launch_path = dep_proj_dir + '/.vscode/launch.json'
        if os.path.exists(tasks_path):
            log.info('  deleting {}'.format(tasks_path))
            os.remove(tasks_path)
        if os.path.exists(launch_path):
            log.info('  deleting {}'.format(launch_path))
            os.remove(launch_path)

#-------------------------------------------------------------------------------
def write_workspace_settings(fips_dir, proj_dir, cfg, proj_settings):
    '''write the VSCode launch.json, tasks.json and
    c_cpp_properties.json files from cmake output files
    '''
    log.info("=== writing Visual Studio Code config files...")
    vscode_dir = proj_dir + '/.vscode'
    if not os.path.isdir(vscode_dir):
        os.makedirs(vscode_dir)
    # fetch all project dependencies
    success, impex = dep.get_all_imports_exports(fips_dir, proj_dir)
    if not success :
        log.warn("missing import project directories, please run 'fips fetch'")
    remove_vscode_tasks_launch_files(fips_dir, proj_dir, impex, cfg)
    write_launch_json(fips_dir, proj_dir, vscode_dir, cfg, proj_settings)
    write_code_workspace_file(fips_dir, proj_dir, impex, cfg)

#-------------------------------------------------------------------------------
def cleanup(fips_dir, proj_dir):
    '''goes through all dependencies and deletes the .vscode directory'''
    # fetch all project dependencies
    success, impex = dep.get_all_imports_exports(fips_dir, proj_dir)
    if not success :
        log.warn("missing import project directories, please run 'fips fetch'")
    log.info(log.RED + 'Please confirm to delete the following directories:' + log.DEF)
    for dep_proj_name in reversed(impex):
        dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
        vscode_dir = dep_proj_dir + '/.vscode/'
        if os.path.isdir(vscode_dir):
            log.info('  {}'.format(vscode_dir))
    if util.confirm(log.RED + 'Delete those directories?' + log.DEF):
        for dep_proj_name in reversed(impex):
            dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
            vscode_dir = dep_proj_dir + '/.vscode/'
            if os.path.isdir(vscode_dir):
                log.info('  deleting {}'.format(vscode_dir))
                shutil.rmtree(vscode_dir)
        log.info('Done.')
    else:
        log.info('Nothing deleted, done.')
