'''this is just a dummy tool to check if the VSCode C/C++ Extension is installed'''
import subprocess
import platform

name = 'vscode-cpptools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """
    Checks if the VSCode MS C/C++ extension is installed
    """
    try:
        if platform.system() == 'Windows':
            res = subprocess.check_output('code --list-extensions', shell=True).decode('utf-8')
        else:
            res = subprocess.check_output(['code', '--list-extensions']).decode('utf-8')
        return 'ms-vscode.cpptools' in res
    except (OSError, subprocess.CalledProcessError):
        return False
