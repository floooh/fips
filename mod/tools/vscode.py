'''VSCode helper functions'''
import platform, subprocess, os, json, shutil, copy
from mod import util, log, dep

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
    return build_tool == 'vscode'

#------------------------------------------------------------------------------
def run(proj_dir):
    exe = exe_name()
    proj_name = util.get_project_name_from_dir(proj_dir)
    try:
        subprocess.call('{} .vscode/{}.code-workspace'.format(exe, proj_name), cwd=proj_dir, shell=True)
    except OSError:
        log.error("Failed to run Visual Studio Code as '{}'".format(exe))

#-------------------------------------------------------------------------------
def has_extension(name):
    try:
        if platform.system() == 'Windows':
            res = subprocess.check_output('code --list-extensions', shell=True).decode('utf-8')
        else:
            res = subprocess.check_output(['code', '--list-extensions']).decode('utf-8')
        return name in res
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def write_launch_json(fips_dir, proj_dir, vscode_dir, cfg, proj_settings):
    '''write the .vscode/launch.json file'''
    launch = {
        'version': '0.2.0',
        'configurations': []
    }
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    host_platform = util.get_host_platform()

    if cfg['platform'] == 'emscripten':
        # Emscripten/WASM (assumes browser runtime environment, not WASI)
        launch['configurations'].append({
            'type': 'chrome',
            'request': 'launch',
            'name': 'Debug in Chrome',
            'url': 'http://localhost:8080/${command:cmake.launchTargetFilename}',
            'server': {
                'program': f'{build_dir}/httpserver.js'
            }
        })
    else:
        # native platforms
        launch_config = {
            'request': 'launch',
            'program': '${command:cmake.launchTargetPath}',
            'cwd': deploy_dir,
            'args': [],
        }
        if host_platform == 'win':
            launch_config['type'] = 'cppvsdbg'
        elif host_platform == 'linux':
            launch_config['type'] = 'cppdbg'
            launch_config['MIMode'] = 'gdb'
        else:
            # NOTE: sometimes the MS C++ Extensions debugger is problematic on macOS,
            # in that case, keep the codelldb extension around as fallback
            #launch_config['type'] = 'lldb'
            launch_config['type'] = 'cppdbg'
            launch_config['MIMode'] = 'lldb'

        launch_config['name'] = 'Debug Current Target'
        launch['configurations'].append(copy.deepcopy(launch_config))

        launch_config['name'] = 'Debug Current Target (Stop at Entry)'
        if launch_config['type'] == 'lldb':
            launch_config['stopOnEntry'] = True
        else:
            launch_config['stopAtEntry'] = True
        launch['configurations'].append(copy.deepcopy(launch_config))

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
def write_httpserver_helper(fips_dir, proj_dir, cfg):
    '''writes a httpserver.js helper script to the build directory
    which is used by the vscode launch.json for Emscripten targets
    '''
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    path = f"{build_dir}/httpserver.js"

    src  =  "const { execSync } = require('child_process');\n"
    src +=  "execSync('http-server -c-1 -g .', {\n"
    src += f"  cwd: '{deploy_dir}',\n"
    src +=  "  stdio: 'inherit',\n"
    src +=  "  stderr: 'inherit',\n"
    src +=  "});\n"
    log.info(f"  writing {path}")
    with open(path, 'w') as f:
        f.write(src)

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
    if (cfg['platform'] == 'emscripten'):
        write_httpserver_helper(fips_dir, proj_dir, cfg)

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
