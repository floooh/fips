'''VSCode helper functions'''
import platform,subprocess, os, yaml, json, inspect, tempfile, glob, shutil
from mod import util,log,verb,dep
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

#------------------------------------------------------------------------------
def read_cmake_targets(fips_dir, proj_dir, cfg, types):
    '''Reads the fips_targets.yml file which was created during
    "fips gen", and extract targets matching the target
    types in the types array, or if types is None, all targets.
    '''
    success, targets = util.get_cfg_target_list(fips_dir, proj_dir, cfg)
    if success:
        if types:
            matching_targets = [tgt for tgt in targets if targets[tgt] in types]
        else:
            matching_targets = targets.keys()
        return matching_targets
    else:
        log.error('Failed to read fips_targets.yml from build dir')
        return None

#------------------------------------------------------------------------------
def read_cmake_headerdirs(fips_dir, proj_dir, cfg):
    '''reads the fips_headerdirs.yml file which was created during
    "fips gen" and returns a list of unique include paths
    '''
    result = []
    success, dirs = util.get_cfg_headersdirs_by_target(fips_dir, proj_dir, cfg)
    if success:
        for _,val in dirs.items():
            result.extend(val)
    return set(result)

#-------------------------------------------------------------------------------
def read_cmake_defines(fips_dir, proj_dir, cfg):
    '''reads the fips_defines.yml file which was created during
    "fips gen" and returns map of unique top-level defines.
    '''
    result = []
    success, defs = util.get_cfg_defines_by_target(fips_dir, proj_dir, cfg)
    if success:
        log.info('     defines from cmake:')
        for _,val in defs.items():
            if val:
                for define in val:
                    if define not in result:
                        result.append(define)
                        log.info('       {}'.format(define))
    if 'vscode_additional_defines' in cfg:
        log.info('     defines from build config (vscode_additional_defines):')
        for define in cfg['vscode_additional_defines']:
            if define not in result:
                result.append(define)
                log.info('       {}'.format(define))
    else:
        log.info('     no additional defines from build config (vscode_additional_defines)')
    return result

#-------------------------------------------------------------------------------
def problem_matcher():
    # FIXME: an actual compiler identification would be better here!
    if util.get_host_platform() == 'win':
        # assume that Windows is always the Visual Studio compiler
        return "$msCompile"
    else:
        return {
            'owner': 'cpp',
            'fileLocation': 'absolute',
            'pattern': {
                'regexp': '^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$',
                'file': 1,
                'line': 2,
                'column': 3,
                'severity': 4,
                'message': 5
            }
        }

#-------------------------------------------------------------------------------
def get_cc_header_paths():
    '''runs "cc -E -xc++ -v dummy.cc" and extract the header search
    path from stdout, return these as array of strings.
    '''
    if util.get_host_platform() not in ['osx','linux']:
        return []
    
    # write a dummy C source file
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(b'int main() {return 0;}')
    tmp.close()

    # run clang in preprocessor mode
    outp = subprocess.check_output(['cc', '-E', '-xc++', '-v', tmp.name], stderr=subprocess.STDOUT).decode("utf-8")

    # delete the temp source file
    os.remove(tmp.name)

    # find the header search paths
    result = []
    capture = False
    for line in outp.splitlines():
        if line == '#include <...> search starts here:':
            # start capturing lines
            capture = True
            continue
        if line == 'End of search list.':
            # finish capturing
            break
        if capture:
            l = line.replace('(framework directory)', '').strip()
            result.append(l)
    return result

#------------------------------------------------------------------------------
def get_vs_header_paths(fips_dir, proj_dir, cfg):
    '''hacky way to find the header search path in the latest installed
    Windows 10 Kit and Visual Studio instance
    '''
    if util.get_host_platform() != 'win':
        return []

    # Windows system headers are in 2 locations, first find the latest Windows Kit
    result = []
    kits = glob.glob('C:/Program Files (x86)/Windows Kits/10/Include/*/')
    if kits:
        latest = max(kits).replace('\\','/')
        subdirs = glob.glob(latest + '/*/')
        for d in subdirs:
            result.append(d.replace('\\','/'))

    # next get the used active Visual Studio instance from the cmake cache
    proj_name = util.get_project_name_from_dir(proj_dir)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    outp = subprocess.check_output(['cmake', '-LA', '-N', '.'], cwd=build_dir).decode("utf-8")
    for line in outp.splitlines():
        if line.startswith('CMAKE_LINKER:FILEPATH='):
            bin_index = line.find('/bin/')
            if bin_index > 0:
                result.append(line[22:bin_index+1]+'include')
    return result

#------------------------------------------------------------------------------
def list_extensions() :
    '''queries Visual Studio Code for installed extensions
    :returns:   list of extensions
    '''
    try:
        outp = subprocess.check_output('{} --list-extensions'.format(exe_name()), shell=True).decode("utf-8")
        return outp.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return []

#-------------------------------------------------------------------------------
def write_tasks_json(fips_dir, proj_dir, vscode_dir, cfg):
    '''write the .vscode/tasks.json file'''
    all_targets = read_cmake_targets(fips_dir, proj_dir, cfg, None)
    tasks = {
        'version': '2.0.0',
        'type': 'shell',
        'presentation': {
            'reveal': 'always',
            'clear':True
        },
        'tasks': []
    }
    # write the actual tasks
    for tgt in all_targets:
        tasks['tasks'].append({
            'label': tgt,
            'command': 'python fips make {}'.format(tgt),
            'group': 'build',
            'problemMatcher': [ problem_matcher() ],
        })
    tasks['tasks'].append({
        'label': 'ALL',
        'command': 'python fips build',
        'group': {
            'kind': 'build',
            'isDefault': True
        },
        'problemMatcher': [ problem_matcher() ],
    })
    task_path = vscode_dir + '/tasks.json'
    with open(task_path, 'w') as f:
        json.dump(tasks, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def write_launch_json(fips_dir, proj_dir, vscode_dir, cfg):
    '''write the .vscode/launch.json file'''
    proj_name = util.get_project_name_from_dir(proj_dir)
    exe_targets = read_cmake_targets(fips_dir, proj_dir, cfg, ['app'])
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])

    pre_launch_build_options = [('', True), (' [Skip Build]', False)]
    stop_at_entry_options = [('', False), (' [Stop At Entry]', True)]

    launch = {
        'version': '0.2.0',
        'configurations': []
    }
    for tgt in exe_targets:
        for pre_launch_build in pre_launch_build_options:
            for stop_at_entry in stop_at_entry_options:
                path = deploy_dir + '/' + tgt
                if util.get_host_platform() == 'win':
                    path += '.exe'
                cwd = util.lookup_target_cwd(proj_dir, tgt)
                if cwd == None:
                    cwd = os.path.dirname(path)
                osx_path = path + '.app/Contents/MacOS/' + tgt
                osx_cwd = os.path.dirname(osx_path)
                if os.path.isdir(osx_cwd):
                    path = osx_path
                    cwd = osx_cwd
                if util.get_host_platform() == 'win':
                    c = {
                        'name': tgt + pre_launch_build[0] + stop_at_entry[0],
                        'type': 'cppvsdbg',
                        'request': 'launch',
                        'program': path,
                        'args': [],
                        'stopAtEntry': stop_at_entry[1],
                        'cwd': cwd,
                        'environment': [],
                        'externalConsole': False,
                        'preLaunchTask': tgt if pre_launch_build[1] else ''
                    }
                elif util.get_host_platform() == 'linux':
                    c = {
                        'name': tgt + pre_launch_build[0] + stop_at_entry[0],
                        'type': 'cppdbg',
                        'request': 'launch',
                        'program': path,
                        'args': [],
                        'stopAtEntry': stop_at_entry[1],
                        'cwd': cwd,
                        'externalConsole': False,
                        'MIMode': 'gdb',
                        'preLaunchTask': tgt if pre_launch_build[1] else ''
                    }
                else:
                    c = {
                        'name': tgt + pre_launch_build[0] + stop_at_entry[0],
                        'type': 'cppdbg',
                        'request': 'launch',
                        'program': path,
                        'args': [],
                        'stopAtEntry': stop_at_entry[1],
                        'cwd': cwd,
                        'externalConsole': False,
                        'MIMode': 'lldb',
                        'preLaunchTask': tgt if pre_launch_build[1] else ''
                    }
                launch['configurations'].append(c)

    # add a python code-generator debug config
    c = {
        'name': 'fips codegen',
        'type': 'python',
        'request': 'launch',
        'stopOnEntry': True,
        'pythonPath': '${config:python.pythonPath}',
        'program': build_dir + '/fips-gen.py',
        'args': [ build_dir + '/fips_codegen.yml' ],
        "cwd": proj_dir,
        "debugOptions": [
            "WaitOnAbnormalExit",
            "WaitOnNormalExit",
            "RedirectOutput"
        ]
    }
    launch['configurations'].append(c)

    # add a python debug config for each fips verb
    for verb_name, verb_mod in verb.verbs.items() :
        # ignore standard verbs
        if fips_dir not in inspect.getfile(verb_mod):
            c = {
                'name': 'fips {}'.format(verb_name),
                'type': 'python',
                'request': 'launch',
                'stopOnEntry': True,
                'pythonPath': '${config:python.pythonPath}',
                'program': proj_dir + '/fips',
                'args': [ verb_name ],
                'cwd': proj_dir,
                "debugOptions": [
                    "WaitOnAbnormalExit",
                    "WaitOnNormalExit",
                    "RedirectOutput"
                ]
            }
            launch['configurations'].append(c)
    launch_path = vscode_dir + '/launch.json'
    log.info('  writing {}'.format(launch_path))
    with open(launch_path, 'w') as f:
        json.dump(launch, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def write_c_cpp_properties_json(fips_dir, proj_dir, impex, cfg):
    '''write the .vscode/c_cpp_properties.json files for main project
       and all dependent projects
    '''
    proj_name = util.get_project_name_from_dir(proj_dir)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    defines = read_cmake_defines(fips_dir, proj_dir, cfg)
    compile_commands_path = build_dir + '/compile_commands.json'
    has_compile_command_json = os.path.isfile(compile_commands_path)
    inc_paths = None
    if not has_compile_command_json:
        inc_paths = read_cmake_headerdirs(fips_dir, proj_dir, cfg)
    props = {
        'configurations': [],
        'version': 3
    }
    for config_name in ['Mac','Linux','Win32']:
        c = {
            'name': config_name,
            'browse': {
                'limitSymbolsToIncludedHeaders': True,
                'databaseFilename': '{}/browse.VS.code'.format(build_dir)
            }
        }
        config_incl_paths = None
        compiler_path = None
        intellisense_mode = 'clang-x64'
        if config_name == 'Mac':
            if not has_compile_command_json:
                config_incl_paths = get_cc_header_paths()
            config_defines = ['_DEBUG','__GNUC__','__APPLE__','__clang__']
            compiler_path = '/usr/bin/c++'
        elif config_name == 'Linux':
            if not has_compile_command_json:
                config_incl_paths = get_cc_header_paths()
            config_defines = ['_DEBUG','__GNUC__']
            compiler_path = '/usr/bin/c++'
        else:
            if not has_compile_command_json:
                config_incl_paths = get_vs_header_paths(fips_dir, proj_dir, cfg)
            intellisense_mode = 'msvc-x64'
            config_defines = ['_DEBUG','_WIN32']
        if inc_paths:
            config_incl_paths.extend(inc_paths)
        config_defines.extend(defines)
        
        if compiler_path:
            c['compilerPath'] = compiler_path
        if has_compile_command_json:
            c['compileCommands'] = compile_commands_path
        if config_incl_paths:
            c['includePath'] = config_incl_paths
        c['defines'] = config_defines
        if config_incl_paths:
            c['browse']['path'] = config_incl_paths
        c['intelliSenseMode'] = intellisense_mode
        props['configurations'].append(c)
    
    # add dependencies in reverse order, so that main project is first
    for dep_proj_name in reversed(impex):
        dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
        vscode_dir = dep_proj_dir + '/.vscode'
        if not os.path.isdir(vscode_dir):
            os.makedirs(vscode_dir)
        prop_path = vscode_dir + '/c_cpp_properties.json'
        log.info('  writing {}'.format(prop_path))
        with open(prop_path, 'w') as f:
            json.dump(props, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def write_cmake_tools_settings(fips_dir, proj_dir, vscode_dir, cfg):
    '''write a settings.json for CMakeTools plugin settings'''
    proj_name = util.get_project_name_from_dir(proj_dir)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
    settings = {
        'cmake.buildDirectory': build_dir,
        'cmake.configureSettings': {
            'FIPS_CONFIG:': cfg['name']
        }
    }
    settings_path = vscode_dir + '/settings.json' 
    log.info('  writing {}'.format(settings_path))
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=1, separators=(',',':'))

#-------------------------------------------------------------------------------
def write_code_workspace_file(fips_dir, proj_dir, impex, cfg):
    '''write a multiroot-workspace config file'''
    vscode_dir = proj_dir + '/.vscode'
    ws = {
        'folders': [],
        'settings': {}
    }
    # add dependencies in reverse order, so that main project is first
    for dep_proj_name in reversed(impex):
        dep_proj_dir = util.get_project_dir(fips_dir, dep_proj_name)
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
def write_workspace_settings(fips_dir, proj_dir, cfg):
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
    vscode_extensions = list_extensions()
    has_cmake_tools = any('vector-of-bool.cmake-tools' in ext for ext in vscode_extensions)
    remove_vscode_tasks_launch_files(fips_dir, proj_dir, impex, cfg)
    write_tasks_json(fips_dir, proj_dir, vscode_dir, cfg)
    write_launch_json(fips_dir, proj_dir, vscode_dir, cfg)
    if has_cmake_tools:
        write_cmake_tools_settings(fips_dir, proj_dir, vscode_dir, cfg)
    else:
        write_c_cpp_properties_json(fips_dir, proj_dir, impex, cfg)
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
