'''this is just a dummy tool to check if the VSCode CodeLLDB Extension is installed'''
import subprocess
import platform

name = 'vscode-codelldb'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """
    Checks if the VSCode CodeLLDB extension is installed
    """
    try:
        if platform.system() == 'Windows':
            res = subprocess.check_output('code --list-extensions', shell=True).decode('utf-8')
        else:
            res = subprocess.check_output(['code', '--list-extensions']).decode('utf-8')
        return 'vadimcn.vscode-lldb' in res
    except (OSError, subprocess.CalledProcessError):
        return False
