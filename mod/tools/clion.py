'''CLion helper functions'''
import subprocess, os, shutil
from mod import util, log, verb, dep
from mod.tools import cmake
from distutils.spawn import find_executable

name = 'clion'
platforms = ['osx','linux','win']
optional = True
not_found = 'used as IDE with clion configs'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if 'clion' is in the path
    :returns:   True if clion is in the path
    """
    host = util.get_host_platform()
    if host == 'linux':
        # See if CLion was installed from a tar.gz and manually added to the path ("clion.sh"),
        # or added to the path using the "create launcher" command in CLion, which would by default
        # create a symlink from clion.sh to /usr/local/bin/clion.
        # This will also pick up CLion if it was installed using snap.
        if find_executable("clion.sh") is not None or find_executable("clion") is not None:
            return True
        else:
            return False
    elif host == 'osx':
        try:
            subprocess.check_output("mdfind -name CLion.app | grep 'CLion'", shell=True)
            return True
        except (OSError, subprocess.CalledProcessError):
            return False
    else:
        return False

#------------------------------------------------------------------------------
def match(build_tool):
    return build_tool == 'clion'

#------------------------------------------------------------------------------
def run(proj_dir):
    host = util.get_host_platform()
    if host == 'linux':
        try:
            if find_executable("clion.sh") is not None:
                subprocess.Popen('clion.sh {}'.format(proj_dir), cwd=proj_dir, shell=True)
            else:
                subprocess.Popen('clion {}'.format(proj_dir), cwd=proj_dir, shell=True)
        except OSError:
            log.error("Failed to run JetBrains CLion as 'clion' or 'clion.sh'")
    elif host == 'osx':
        try:
            subprocess.Popen('open /Applications/CLion.app --args {}'.format(proj_dir), cwd=proj_dir, shell=True)
        except OSError:
            log.error("Failed to run JetBrains CLion as '/Applications/CLion.app'")
    else:
        log.error("Not supported on this platform")

#-------------------------------------------------------------------------------
def write_clion_module_files(fips_dir, proj_dir, cfg):
    '''write misc.xml, modules.xml, *.iml'''
    proj_name = util.get_project_name_from_dir(proj_dir)
    iml_path = '{}/.idea/{}.iml'.format(proj_dir, proj_name)
    if os.path.exists(iml_path):
        return
    with open(iml_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<module classpath="CMake" type="CPP_MODULE" version="4" />')
    ws_path = '{}/.idea/misc.xml'.format(proj_dir)
    with open(ws_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<project version="4">\n')
        f.write('  <component name="CMakeWorkspace" IGNORE_OUTSIDE_FILES="true" PROJECT_DIR="$PROJECT_DIR$" />\n')
        f.write('</project>')
    ws_path = '{}/.idea/modules.xml'.format(proj_dir)
    with open(ws_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<project version="4">\n')
        f.write('  <component name="ProjectModuleManager">\n')
        f.write('    <modules>\n')
        f.write('      <module fileurl="file://$PROJECT_DIR$/.idea/{}.iml" filepath="$PROJECT_DIR$/.idea/{}.iml" />\n'.format(proj_name, proj_name))
        f.write('    </modules>\n')
        f.write('  </component>\n')
        f.write('</project>')

#-------------------------------------------------------------------------------
def write_clion_workspace_file(fips_dir, proj_dir, cfg):
    '''write bare-bone workspace.xml config file'''
    proj_name = util.get_project_name_from_dir(proj_dir)
    gen_options = '-DFIPS_CONFIG={}'.format(cfg['name'])
    gen_dir = '$PROJECT_DIR$/../fips-build/{}/{}'.format(proj_name, cfg['name'])
    ws_path = '{}/.idea/workspace.xml'.format(proj_dir)
    # do not overwrite existing .xml
    if os.path.exists(ws_path):
        return
    with open(ws_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<project version="4">\n')
        # TODO: CMakeRunConfigurationManager
        f.write('  <component name="CMakeSettings">\n')
        f.write('    <configurations>\n')
        f.write('      <configuration PROFILE_NAME="Debug" CONFIG_NAME="Debug" GENERATION_OPTIONS="{}" GENERATION_DIR="{}" />\n'.format(gen_options, gen_dir))
        f.write('    </configurations>\n')
        f.write('  </component>\n')
        # TODO: RunManager
        f.write('</project>')

#-------------------------------------------------------------------------------
def write_workspace_settings(fips_dir, proj_dir, cfg):
    '''write the CLion *.xml files required to open the project
    '''
    log.info("=== writing JetBrains CLion config files...")
    clion_dir = proj_dir + '/.idea'
    if not os.path.isdir(clion_dir):
        os.makedirs(clion_dir)
    write_clion_module_files(fips_dir, proj_dir, cfg)
    write_clion_workspace_file(fips_dir, proj_dir, cfg)

#-------------------------------------------------------------------------------
def cleanup(fips_dir, proj_dir):
    '''deletes the .idea directory'''
    clion_dir = proj_dir + '/.idea'
    if os.path.isdir(clion_dir):
        log.info(log.RED + 'Please confirm to delete the following directory:' + log.DEF)
        log.info('  {}'.format(clion_dir))
        if util.confirm(log.RED + 'Delete this directory?' + log.DEF):
            if os.path.isdir(clion_dir):
                log.info('  deleting {}'.format(clion_dir))
                shutil.rmtree(clion_dir)
            log.info('Done.')
        else:
            log.info('Nothing deleted, done.')
    else:
        log.info('Nothing to delete.')
