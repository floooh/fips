from sys import version_info
if version_info[0] < 3:
    from yaml.yaml2 import *
else:
    from yaml.yaml3 import *
