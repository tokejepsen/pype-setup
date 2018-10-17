import os
import sys
import subprocess

from .. import logger

Logger = logger()
log = Logger.getLogger(__name__)
PYPE_DEBUG = bool(os.getenv("PYPE_DEBUG"))


def get_conf_file(
    dir,
    root_file_name,
    preset_name=None,
    split_pattern=None,
    representation=None
):
    '''Gets any available `config template` file from given
    **path** and **name**

    Attributes:
        dir (str): path to root directory where files could be searched
        root_file_name (str): root part of name it is searching for
        preset_name (str): default preset name
        split_pattern (str): default pattern for spliting name and preset
        representation (str): extention of file used for config files
                              can be ".toml" but also ".conf"

    Returns:
        file_name (str): if matching name found or None
    '''

    if not preset_name:
        preset_name = "default"
    if not split_pattern:
        split_pattern = ".."
    if not representation:
        representation = ".toml"

    conf_file = root_file_name + representation
    # print(dir, root_file_name, preset_name,
    # split_pattern, representation)
    try:
        preset = os.environ["PYPE_TEMPLATES_PRESET"]
    except KeyError:
        preset = preset_name

    test_files = [
        f for f in os.listdir(dir)
        if split_pattern in f
    ]

    try:
        conf_file = [
            f for f in test_files
            if preset in os.path.splitext(f)[0].split(split_pattern)[1]
            if root_file_name in os.path.splitext(f)[0].split(split_pattern)[0]
        ][0]
    except IndexError as error:
        if PYPE_DEBUG:
            log.warning("File is missing '{}' will be"
                        "used basic config file: {}".format(
                            error, conf_file
                        ))
        pass

    return conf_file if os.path.exists(os.path.join(dir, conf_file)) else None


def forward(args, silent=False, cwd=None):
    """Pass `args` to the Avalon CLI, within the Avalon Setup environment

    Arguments:
        args (list): Command-line arguments to run
            within the active environment

    """

    if PYPE_DEBUG:
        print("Forwarding '%s'.." % " ".join(args))

    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd
    )

    # Blocks until finished
    while True:
        line = popen.stdout.readline()
        if line != '':
            if not silent or PYPE_DEBUG:
                sys.stdout.write(line)
        else:
            break

    if PYPE_DEBUG:
        print("avalon.py: Finishing up..")

    popen.wait()
    return popen.returncode
