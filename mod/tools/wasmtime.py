import subprocess

name = 'wasmtime'
platforms = ['linux', 'osx', 'win']
optional = True
not_found = "required for running WASI executables"

#-------------------------------------------------------------------------------
def check_exists(fips_dir):
    try:
        out = subprocess.check_output(['wasmtime', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

#-------------------------------------------------------------------------------
def run(proj_dir, deploy_dir, target_name, target_args, target_cwd):
    cmd_line = 'wasmtime --dir . {}/{}.wasm -- {}'.format(deploy_dir, target_name, ' '.join(target_args))
    subprocess.call(cmd_line, shell=True)
