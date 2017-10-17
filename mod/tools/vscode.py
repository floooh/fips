'''VSCode helper functions'''
import subprocess
import os
import yaml
import json
import inspect
import tempfile
from mod import util,log,verb
from mod.tools import cmake

name = 'vscode'
platforms = ['osx','linux','win']
optional = True
not_found = 'used as IDE with vscode configs'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if 'code' is in the path
    :returns:   True if code is in the path
    """
    try:
        subprocess.check_output('code -version', shell=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#------------------------------------------------------------------------------
def run(proj_dir):
    try:
        subprocess.call('code .', cwd=proj_dir, shell=True)
    except OSError:
        log.error("Failed to run Visual Studio Code as 'code'") 

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
    "fips gen" and returns a list of unique header search paths
    '''
    result = []
    success, dirs = util.get_cfg_headersdirs_by_target(fips_dir, proj_dir, cfg)
    if success:
        for _,dirs in dirs.items():
            result.extend(dirs)
    return set(result)

#------------------------------------------------------------------------------
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
def get_clang_header_paths():
    '''runs "clang -E -xc++ -v dummy.cc" and extract the header search
    path from stdout, return these as array of strings.
    '''
    if util.get_host_platform() != 'osx':
        return []
    
    # write a dummy C source file
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write('int main() {return 0;}')
    tmp.close()

    # run clang in preprocessor mode
    outp = subprocess.check_output(['clang', '-E', '-xc++', '-v', tmp.name], stderr=subprocess.STDOUT)

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

#-------------------------------------------------------------------------------
def write_workspace_settings(fips_dir, proj_dir, cfg):
    '''write the VSCode launch.json, tasks.json and
    c_cpp_properties.json files from cmake output files
    '''
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg)
    vscode_dir = proj_dir + '/.vscode'
    if not os.path.isdir(vscode_dir):
        os.makedirs(vscode_dir)
    exe_targets = read_cmake_targets(fips_dir, proj_dir, cfg, ['app'])
    all_targets = read_cmake_targets(fips_dir, proj_dir, cfg, None)
    inc_paths = read_cmake_headerdirs(fips_dir, proj_dir, cfg)

    if util.get_host_platform() == 'win':
        fips_cmd = 'fips'
    else:
        fips_cmd = './fips'

    # write a tasks.json file
    tasks = {
        'version':  '0.1.0',
        'command':  fips_cmd,
        'isShellCommand':   True,
        'showOutput': 'silent',
        'suppressTaskName': True,
        'echoCommand': True,
        'tasks': []
    }
    for tgt in all_targets:
        tasks['tasks'].append({
            'taskName': tgt,
            'args': ['make', tgt],
            'problemMatcher': problem_matcher(),
        })
    tasks['tasks'].append({
        'isBuildCommand': True,
        'taskName': 'ALL',
        'args': ['build'],
        'problemMatcher': problem_matcher()
    })
    with open(vscode_dir + '/tasks.json', 'w') as f:
        json.dump(tasks, f, indent=1, separators=(',',':'))

    # write a launch.json with 1 config per build target
    launch = {
        'version': '0.2.0',
        'configurations': []
    }
    for tgt in exe_targets:
        path = deploy_dir + '/' + tgt
        if util.get_host_platform() == 'win':
            path += '.exe'
        cwd = os.path.dirname(path)
        osx_path = path + '.app/Contents/MacOS/' + tgt
        osx_cwd = os.path.dirname(osx_path)
        if os.path.isdir(osx_cwd):
            path = osx_path
            cwd = osx_cwd
        if util.get_host_platform() == 'win':
            c = {
                'name': tgt,
                'type': 'cppvsdbg',
                'request': 'launch',
                'program': path,
                'args': [],
                'stopAtEntry': True,
                'cwd': cwd,
                'environment': [],
                'externalConsole': False
            }
        elif util.get_host_platform() == 'linux':
            c = {
                'name': tgt,
                'type': 'cppdbg',
                'request': 'launch',
                'program': path,
                'args': [],
                'stopAtEntry': True,
                'cwd': cwd,
                'externalConsole': False,
                'MIMode': 'gdb'
            }
        else:
            c = {
                'name': tgt,
                'type': 'cppdbg',
                'request': 'launch',
                'program': path,
                'args': [],
                'stopAtEntry': True,
                'cwd': cwd,
                'externalConsole': False,
                'MIMode': 'lldb'
            }
        launch['configurations'].append(c)

    # add a python code-generator debug config
    c = {
        'name': 'fips codegen',
        'type': 'python',
        'request': 'launch',
        'stopOnEntry': True,
        'pythonPath': '${config:python.pythonPath}',
        'program': proj_dir + '/.fips-gen.py',
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

    with open(vscode_dir + '/launch.json', 'w') as f:
        json.dump(launch, f, indent=1, separators=(',',':'))

    # write a c_cpp_properties.json file with header-search paths
    props = {
        'configurations': []
    }
    for config_name in ['Mac','Linux','Win32']:
        c = {
            'name': config_name,
            'browse': {
                'limitSymbolsToIncludeHeaders': True,
                'databaseFilename': '{}/browse.VS.code'.format(build_dir)
            }
        }
        config_incl_paths = []
        if config_name == 'Mac':
            config_incl_paths = get_clang_header_paths()
        elif config_name == 'Linux':
            config_incl_paths = [
                '/usr/include',
                '/usr/local/include'
            ]
        else:
            config_incl_paths = [
                # FIXME
                'C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/include/*'
            ]
        for inc_path in inc_paths:
            config_incl_paths.append(inc_path)
        c['includePath'] = config_incl_paths
        c['browse']['path'] = config_incl_paths
        props['configurations'].append(c)
    with open(vscode_dir + '/c_cpp_properties.json', 'w') as f:
        json.dump(props, f, indent=1, separators=(',',':'))
