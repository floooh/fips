'''this is just a dummy tool to check if the VSCode CMake Tools is installed'''
import subprocess

name = 'vscode-cmaketools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """
    Checks if the CMake Tools extension is installed
    """
    try :
        res = subprocess.check_output(['code', '--list-extensions'],
            stderr=subprocess.STDOUT,
            universal_newlines=True) # return string not binary for python 2/3 compatibility
    except (OSError, subprocess.CalledProcessError) :
        return False
    return 'ms-vscode.cmake-tools' in res
