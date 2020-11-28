"""logging functions"""
import sys

# log colors
RED = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;36m'
DEF = '\033[0;0m'

#-------------------------------------------------------------------------------
def error(msg, fatal=True) :
    """
    Print error message and exit with error code 10
    unless 'fatal' is False.

    :param msg:     string message
    :param fatal:   exit program with error code 10 if True (default is true)
    """
    print('{}[ERROR]{} {}'.format(RED, DEF, msg))
    if fatal :
        sys.exit(10)

#-------------------------------------------------------------------------------
def warn(msg) :
    """print a warning message"""
    print('{}[WARNING]{} {}'.format(YELLOW, DEF, msg))

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
def optional(item, status) :
    """print a yellow 'optional' message

    :param item:    first part of message
    :param status:  status (colored yellow)
    """
    print('{}:\t{}{}{}'.format(item, YELLOW, status, DEF))

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

