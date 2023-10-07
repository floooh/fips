'''checks if the VSCode WASM DWARF debugging extension is installed'''
import subprocess
import platform
from mod.tools import vscode

name = 'wasm-dwarf-debugging'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.wasm-dwarf-debugging'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    return vscode.has_extension('ms-vscode.wasm-dwarf-debugging')
