# pylint: disable=import-outside-toplevel

import unittest
import os
import pathlib
import sys
import ensurepip
import subprocess

from textwrap import dedent

main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
sys.path.append(str(main_dir))

def ensure_pip():
    print(dedent('''
        ################################
        ||                            ||
        ||      Ensuring pip...       ||
        ||                            ||
        ################################
    '''))

    ensurepip.bootstrap()
    os.environ.pop("PIP_REQ_TRACKER", None)

def install_dependencies():
    print(dedent('''
        ################################
        ||                            ||
        || Installing dependencies... ||
        ||                            ||
        ################################
    '''))

    python = sys.executable
    dir_path = os.path.dirname(__file__)
    req_file = dir_path + "/../requirements-dev.txt"

    subprocess.run([python, "-m", "pip", "install", "-r", req_file], check=True)

def run_test_suite():
    from test_export import TestExport
    from test_serial_live_mode import TestSerialLiveMode
    from test_socket_live_mode import TestSocketLiveMode

    print(dedent('''
        ################################
        ||                            ||
        ||      Running tests...      ||
        ||                            ||
        ################################
    '''))

    return unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestExport),
        unittest.TestLoader().loadTestsFromTestCase(TestSerialLiveMode),
        unittest.TestLoader().loadTestsFromTestCase(TestSocketLiveMode)
    ])).wasSuccessful()

if __name__ == "__main__":
    ensure_pip()
    install_dependencies()

    successful = run_test_suite()

    if not successful:
        sys.exit(1)
    else:
        sys.exit(0)
