"""logging functions"""
import sys

# log colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
DEF = '\033[0m'

#-------------------------------------------------------------------------------
def error(msg, fatal=True) :
    """
    Print error message and exit with error code 10 
    unless 'fatal' is False.

    :param msg:     string message
    :param fatal:   exit program with error code 10 if True (default is true)
    """
    print('{}[ERROR]{} {}\n'.format(RED, DEF, msg))
    if fatal :
        sys.exit(10)

#-------------------------------------------------------------------------------
def ok(item, status) :
    """print a green 'ok' message

    :param item:    first part of message
    :param status:  status (colored green)
    """
    print('{}:\t{}{}{}'.format(item, GREEN, status, DEF))

#-------------------------------------------------------------------------------
def failed(item, status) :
    """print a red 'fail' message

    :param item:    first part of message
    :param status:  status (colored red)
    """
    print('{}:\t{}{}{}'.format(item, RED, status, DEF))

#-------------------------------------------------------------------------------
def info(msg) :
    """print a normal log message

    :param msg: message
    """
    print(msg)

#-------------------------------------------------------------------------------
def colored(color, msg) :
    """print a colored log message

    :param color:   color escape sequence (e.g. log.YELLOW)
    :param msg:     text message
    """
    print('{}{}{}'.format(color, msg, DEF))

