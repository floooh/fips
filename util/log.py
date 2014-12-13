'''
    logging functions
'''
from util import color

def error(msg) :
    '''
    Print error message and exit with error code 10.
    '''
    print('{}[ERROR]{} {}\n'.format(color.RED, color.DEF, msg))

