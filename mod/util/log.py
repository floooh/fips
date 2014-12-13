'''
    logging functions
'''
import sys
from mod.util import color

def error(msg) :
    '''
    Print error message and continue
    '''
    print('{}[ERROR]{} {}\n'.format(color.RED, color.DEF, msg))
    sys.exit(10)
