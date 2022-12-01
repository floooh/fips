'''this is just a dummy tool to check if the VSCode CMake Tools is installed'''
import subprocess
import platform

name = 'vscode-cmaketools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """
    Checks if the CMake Tools extension is installed
    """
    try:
        if platform.system() == 'Windows':
            res = subprocess.check_output('code --list-extensions', shell=True).decode('utf-8')
        else:
            res = subprocess.check_output(['code', '--list-extensions']).decode('utf-8')
        return 'ms-vscode.cmake-tools' in res
    except (OSError, subprocess.CalledProcessError):
        return False
