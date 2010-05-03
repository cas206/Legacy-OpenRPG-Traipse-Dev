VERSION = "1.8.0"
SERVER_MIN_CLIENT_VERSION = "1.7.1"

#BUILD NUMBER FORMAT: "YYMMDD-##" where ## is the incremental daily build index (if needed)
DISTRO = "Traipse Alpha"
DIS_VER = "Ornery Orc"
BUILD = "100503-01"

# This version is for network capability.
PROTOCOL_VERSION = "1.2"

CLIENT_STRING = DISTRO + ' {' + BUILD + '}'
MENU_TITLE = DISTRO + " " + DIS_VER + ' {' + BUILD + '}'

# These two are used in pyver.py to ensure a minimum python is available
# If the minimum version you want doesn't have a micro (e.g. 2.0), use zero
# for the micro
NEEDS_PYTHON_MAJOR = 2
NEEDS_PYTHON_MINOR = 5
NEEDS_PYTHON_MICRO = 2
