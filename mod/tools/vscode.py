'''VSCode helper functions'''
import subprocess
import os
from mod import util

name = 'vscode'
platforms = ['osx','linux','win']
optional = True
not_found = 'used as IDE with vscode configs'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if 'code' is in the path
    
    :returns:   True if code is in the path
    """
    try :
        subprocess.check_output(['code', '-version'])
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False

#------------------------------------------------------------------------------
def write_workspace_settings(fips_dir, proj_dir, cfg, toolchain_path, defines):
    """write a new VSCode workspace settings file with 
    config settings for the VSCode cmake tools extension.
    """
    vscode_dir = proj_dir + '/.vscode'
    _, targets = util.get_cfg_target_list(fips_dir, proj_dir, cfg)
    proj_name = util.get_project_name_from_dir(proj_dir)
    deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg)
    build_dir = util.get_build_dir(fips_dir, proj_name, cfg)
    if not os.path.isdir(vscode_dir):
        os.makedirs(vscode_dir)

    # write a tasks.json file
    with open(vscode_dir + '/tasks.json', 'w') as f:
        f.write('{\n')
        f.write('\t"version": "0.1.0",\n')
        f.write('\t"command": "./fips",\n')
        f.write('\t"isShellCommand": true,\n')
        f.write('\t"showOutput": "always",\n')
        f.write('\t"suppressTaskName": true,\n')

        # write gcc/clang problem matcher
        f.write('\t"problemMatcher": {\n')
        f.write('\t\t"fileLocation": ["absolute"],\n')
        f.write('\t\t"pattern": {\n')
        f.write('\t\t\t"regexp": "^(.*):(\\\\d+):(\\\\d+):\\\\s+(warning|error):\\\\s+(.*)$",\n')
        f.write('\t\t\t"file": 1,\n')
        f.write('\t\t\t"line": 2,\n')
        f.write('\t\t\t"column": 3,\n')
        f.write('\t\t\t"severity": 4,\n')
        f.write('\t\t\t"message": 5\n')
        f.write('\t\t}\n')
        f.write('\t},\n')

        f.write('\t"tasks": [\n')
        for tgt_name,tgt_type in targets.iteritems():
            f.write('\t\t{\n')
            f.write('\t\t\t"taskName": "{}",\n'.format(tgt_name))
            f.write('\t\t\t"args": ["make", "{}"]\n'.format(tgt_name))
            f.write('\t\t},\n')

        # make ALL task
        f.write('\t\t{\n')
        f.write('\t\t\t"isBuildCommand": true,\n')
        f.write('\t\t\t"taskName": "ALL",\n')
        f.write('\t\t\t"args": ["build"]\n')
        f.write('\t\t},\n')

        # make clean task
        f.write('\t\t{\n')
        f.write('\t\t\t"taskName": "CLEAN",\n')
        f.write('\t\t\t"args": ["clean"]\n')
        f.write('\t\t}\n')
        f.write('\t],\n')
        f.write('\t"echoCommand": true\n')
        f.write('}\n')

    # write a launch.json with 1 config per build target
    with open(vscode_dir + '/launch.json', 'w') as f:
        first = True
        f.write('{\n')
        f.write('\t"version": "0.2.0",\n')
        f.write('\t"configurations": [\n')
        for tgt_name,tgt_type in targets.iteritems():
            if tgt_type == 'app':
                if first:
                    first = False
                else:
                    f.write('\t,\n')
                f.write('\t\t{\n')
                f.write('\t\t\t"type": "lldb",\n')
                f.write('\t\t\t"request": "launch",\n')
                f.write('\t\t\t"name": "{}",\n'.format(tgt_name))
                path = deploy_dir + '/' + tgt_name
                if os.path.isdir(path + '.app'):
                    # special case MacOS
                    path += '.app'
                f.write('\t\t\t"program": "{}"\n'.format(path))
                f.write('\t\t}\n')
        f.write('\t]')
        f.write('}\n')
