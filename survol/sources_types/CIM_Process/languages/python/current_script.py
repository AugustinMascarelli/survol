#!/usr/bin/env python

"""
Current script
"""

import os
import re
import sys
import lib_util
import lib_common
import getopt
from lib_properties import pc
from sources_types import CIM_Process
from sources_types.CIM_Process.languages import python as survol_python

Usable = survol_python.Usable

# usage: python [option] ... [-c cmd | -m mod | file | -] [arg] ...
# Options and arguments (and corresponding environment variables):
# -B     : don't write .py[co] files on import; also PYTHONDONTWRITEBYTECODE=x
# -c cmd : program passed in as string (terminates option list)
# -d     : debug output from parser; also PYTHONDEBUG=x
# -E     : ignore PYTHON* environment variables (such as PYTHONPATH)
# -h     : print this help message and exit (also --help)
# -i     : inspect interactively after running script; forces a prompt even
#          if stdin does not appear to be a terminal; also PYTHONINSPECT=x
# -m mod : run library module as a script (terminates option list)
# -O     : optimize generated bytecode slightly; also PYTHONOPTIMIZE=x
# -OO    : remove doc-strings in addition to the -O optimizations
# -R     : use a pseudo-random salt to make hash() values of various types be
#          unpredictable between separate invocations of the interpreter, as
#          a defense against denial-of-service attacks
# -Q arg : division options: -Qold (default), -Qwarn, -Qwarnall, -Qnew
# -s     : don't add user site directory to sys.path; also PYTHONNOUSERSITE
# -S     : don't imply 'import site' on initialization
# -t     : issue warnings about inconsistent tab usage (-tt: issue errors)
# -u     : unbuffered binary stdout and stderr; also PYTHONUNBUFFERED=x
#          see man page for details on internal buffering relating to '-u'
# -v     : verbose (trace import statements); also PYTHONVERBOSE=x
#          can be supplied multiple times to increase verbosity
# -V     : print the Python version number and exit (also --version)
# -W arg : warning control; arg is action:message:category:module:lineno
#          also PYTHONWARNINGS=arg
# -x     : skip first line of source, allowing use of non-Unix forms of #!cmd
# -3     : warn about Python 3.x incompatibilities that 2to3 cannot trivially fix
# file   : program read from script file
# -      : program read from stdin (default; interactive mode if a tty)
# arg ...: arguments passed to program in sys.argv[1:]
#
# Other environment variables:
# PYTHONSTARTUP: file executed on interactive startup (no default)
# PYTHONPATH   : ';'-separated list of directories prefixed to the
#                default module search path.  The result is sys.path.
# PYTHONHOME   : alternate <prefix> directory (or <prefix>;<exec_prefix>).
#                The default module search path uses <prefix>\lib.
# PYTHONCASEOK : ignore case in 'import' statements (Windows).
# PYTHONIOENCODING: Encoding[:errors] used for stdin/stdout/stderr.
# PYTHONHASHSEED: if this variable is set to 'random', the effect is the same
#    as specifying the -R option: a random value is used to seed the hashes of
#    str, bytes and datetime objects.  It can also be set to an integer
#    in the range [0,4294967295] to get hash values with a predictable seed.

# Find the file, given PYTHONPATH and the process current directory.
def _py_fil_node(proc_obj, fil_nam, ignore_envs):
    full_file_name = None

    if os.path.isabs(fil_nam):
        full_file_name = fil_nam
    else:
        # Check if the file exists in the current directory.
        curr_pwd, err_msg = CIM_Process.PsutilProcCwd(proc_obj)
        if not curr_pwd:
            DEBUG("_py_fil_node: %s",err_msg)
            return None

        all_dirs_to_search = [curr_pwd]

        # With this option, do not use environment variable.
        if not ignore_envs:
            path_python = CIM_Process.GetEnvVarProcess("PYTHONPATH",proc_obj.pid)
            if path_python:
                path_python_split = path_python.split(":")
                all_dirs_to_search += path_python_split

        # Now tries all possible dirs, starting with current directory.
        for a_dir in all_dirs_to_search:
            full_path = os.path.join(a_dir, fil_nam)
            if os.path.isfile(full_path):
                full_file_name = full_path
                break

    if full_file_name:
        fil_node = lib_common.gUriGen.FileUri(full_file_name)
        return fil_node
    else:
        return None


def _add_nodes_from_command_line(argv_array, grph, node_process, proc_obj):
    # First, extracts the executable.
    # This applies to Windows only.
    idx_command = 0
    len_command = len(argv_array)
    if lib_util.isPlatformWindows:
        if argv_array[0].endswith("cmd.exe"):
            idx_command += 1

        while idx_command < len_command and argv_array[idx_command].startswith("/"):
            idx_command += 1

    # Now, the current argument should be a Python command.
    if argv_array[idx_command].find("python") < 0:
        DEBUG("Command does not contain Python:%s", str(argv_array))
        return

    # Now removes options of Python command.
    # Options and arguments (and corresponding environment variables):
    # -B     : don't write .py[co] files on import; also PYTHONDONTWRITEBYTECODE=x
    # -c cmd : program passed in as string (terminates option list)
    # -d     : debug output from parser; also PYTHONDEBUG=x
    # -E     : ignore PYTHON* environment variables (such as PYTHONPATH)
    # -h     : print this help message and exit (also --help)
    # -i     : inspect interactively after running script; forces a prompt even
    #          if stdin does not appear to be a terminal; also PYTHONINSPECT=x
    # -m mod : run library module as a script (terminates option list)
    # -O     : optimize generated bytecode slightly; also PYTHONOPTIMIZE=x
    # -OO    : remove doc-strings in addition to the -O optimizations
    # -R     : use a pseudo-random salt to make hash() values of various types be
    #          unpredictable between separate invocations of the interpreter, as
    #          a defense against denial-of-service attacks
    # -Q arg : division options: -Qold (default), -Qwarn, -Qwarnall, -Qnew
    # -s     : don't add user site directory to sys.path; also PYTHONNOUSERSITE
    # -S     : don't imply 'import site' on initialization
    # -t     : issue warnings about inconsistent tab usage (-tt: issue errors)
    # -u     : unbuffered binary stdout and stderr; also PYTHONUNBUFFERED=x
    #          see man page for details on internal buffering relating to '-u'
    # -v     : verbose (trace import statements); also PYTHONVERBOSE=x
    #          can be supplied multiple times to increase verbosity
    # -V     : print the Python version number and exit (also --version)
    # -W arg : warning control; arg is action:message:category:module:lineno
    #          also PYTHONWARNINGS=arg
    # -x     : skip first line of source, allowing use of non-Unix forms of #!cmd
    # -3     : warn about Python 3.x incompatibilities that 2to3 cannot trivially fix
    # file   : program read from script file
    # -      : program read from stdin (default; interactive mode if a tty)
    # arg ...: arguments passed to program in sys.argv[1:]
    ignore_envs = False
    idx_command += 1
    while idx_command < len_command:
        curr_arg = argv_array[idx_command]
        if curr_arg.startswith("-"):
            if curr_arg == '-E':
                ignore_envs = True
            elif curr_arg in ["-Q","-W"] :
                # Extra argument we do not want.
                idx_command += 1
            elif curr_arg in ["-m"] :
                # TODO: Followed by a module.
                pass
            elif curr_arg in ["-c"] :
                # TODO: Followed by Python code: Cannot anything.
                return
            idx_command += 1
        else:
            fil_node = _py_fil_node(proc_obj, curr_arg, ignore_envs)
            if fil_node:
                grph.add((node_process, pc.property_runs, fil_node))
            break
        idx_command += 1

def Main():
    cgiEnv = lib_common.CgiEnv()
    pid_proc = int(cgiEnv.GetId())

    grph = cgiEnv.GetGraph()

    node_process = lib_common.gUriGen.PidUri(pid_proc)
    proc_obj = CIM_Process.PsutilGetProcObj(int(pid_proc))

    # Now we are parsing the command line.
    argv_array = CIM_Process.PsutilProcToCmdlineArray(proc_obj)

    DEBUG("argv_array=%s",str(argv_array))

    # The difficulty is that filenames with spaces are split.
    # Therefore, entire filenames must be rebuilt from pieces.
    _add_nodes_from_command_line(argv_array, grph, node_process, proc_obj)

    cgiEnv.OutCgiRdf()

if __name__ == '__main__':
    Main()
