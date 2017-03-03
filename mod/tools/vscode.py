'''VSCode helper functions'''
import subprocess
import os
import json
from mod import util,log
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
def extract_targets(codemodel, types):
    '''returns a set of unique target names from the cmake codemodel dump

    :param codemodel: result of cmake.get_codemodel()
    :param types: None: return all target types, or a string array of types
    :returns: list of unique targets
    '''
    result = []
    for config in codemodel['configurations']:
        for project in config['projects']:
            for tgt in project['targets']:
                if types:
                    if tgt['type'] in types:
                        result.append(tgt['name'])
                else:
                    result.append(tgt['name'])
    return set(result)

#------------------------------------------------------------------------------
def extract_include_paths(codemodel):
    '''returns a set of unique include paths from the cmake codemodel dump

    :param codemodel: result of cmake.get_codemodel()
    :returns: list of unique include paths
    '''
    result = []
    for config in codemodel['configurations']:
        for project in config['projects']:
            for tgt in project['targets']:
                if 'fileGroups' in tgt:
                    for fg in tgt['fileGroups']:
                        if 'includePath' in fg:
                            for ip in fg['includePath']:
                                result.append(ip['path'])
    return set(result)

#------------------------------------------------------------------------------
def problem_matcher():
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

#------------------------------------------------------------------------------
def write_workspace_settings(fips_dir, proj_dir, cfg, toolchain_path, defines):
    """parse the cmake-server output file, extract 
    build targets and header search paths, and write
    VSCode config files to .vscode directory
    """
    # first make sure that cmake is new enough to have cmake-server mode
    if not cmake.check_exists(fips_dir, 3, 7):
        log.error("cmake must be at least version 3.7 for VSCode support!")
    vscode_dir = proj_dir + '/.vscode'
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg)
    codemodel = cmake.get_codemodel(fips_dir, proj_dir, cfg)
    all_targets = extract_targets(codemodel, None)
    exe_targets = extract_targets(codemodel, ['EXECUTABLE'])
    inc_paths = extract_include_paths(codemodel)
    if not os.path.isdir(vscode_dir):
        os.makedirs(vscode_dir)

    # write a tasks.json file
    tasks = {
        'version':  '0.1.0',
        'command':  './fips',
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
        cwd = os.path.dirname(path)
        osx_path = path + '.app/Contents/MacOS/' + tgt
        osx_cwd = os.path.dirname(osx_path)
        if os.path.isdir(osx_cwd):
            path = osx_path
            cwd = osx_cwd
        c = {
            'name': tgt,
            'type': 'cppdbg',
            'request': 'launch',
            'program': path,
            'stopAtEntry': True,
            'cwd': cwd,
            'externalConsole': False,
            'linux': {
                'MIMode': 'gdb',
                'setupCommands': [
                    {
                        'description': 'Enable pretty-printing for gdb',
                        'text': '--enable-pretty-printing',
                        'ignoreFailures': True
                    }
                ]
            },
            'osx': {
                'MIMode': 'lldb'
            },
            'windows': {
                'MIMode': 'gdb',
                'setupCommands': [
                    {
                        'description': 'Enable pretty-printing for gdb',
                        'text': '--enable-pretty-printing',
                        'ignoreFailures': True
                    }
                ]
            }
        }
        launch['configurations'].append(c)

    # add a python code-generator debug config
    c = {
        'name': 'fips codegen',
        'type': 'python',
        'request': 'launch',
        'stopOnEntry': True,
        'pythonPath': '${config.python.pythonPath}',
        'program': '.fips-gen.py',
        'args': [ build_dir + '/fips_codegen.yml' ],
        "cwd": proj_dir,
        "debugOptions": [
            "WaitOnAbnormalExit",
            "WaitOnNormalExit",
            "RedirectOutput"
        ]
    }
    launch['configurations'].append(c)

    # TODO: add entries for local fips verbs?

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
                'databaseFilename': ''
            }
        }
        if config_name in ['Mac', 'Linux']:
            c['includePath'] = [
                '/usr/include',
                '/usr/local/include'
            ]
        else:
            c['includePath'] = [
                # FIXME
                'C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/include/*'
            ]
        for inc_path in inc_paths:
            c['includePath'].append(inc_path)
        props['configurations'].append(c)
    with open(vscode_dir + '/c_cpp_properties.json', 'w') as f:
        json.dump(props, f, indent=1, separators=(',',':'))
