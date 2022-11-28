'''this is just a dummy tool to check if the VSCode C/C++ Extension is installed'''
import subprocess

name = 'vscode-cpptools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """
    Checks if the VSCode MS C/C++ extension is installed
    """
    try :
        res = subprocess.check_output(['code', '--list-extensions'],
            stderr=subprocess.STDOUT,
            universal_newlines=True) # return string not binary for python 2/3 compatibility
    except (OSError, subprocess.CalledProcessError) :
        return False
    return 'ms-vscode.cpptools' in res
