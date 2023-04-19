# pylint: disable=wrong-import-position

import unittest
import os
import pathlib
import sys

main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
sys.path.append(str(main_dir))

from test_export import TestExport
from test_serial_live_mode import TestSerialLiveMode
from test_socket_live_mode import TestSocketLiveMode


if __name__ == "__main__":
    successful = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestExport),
        unittest.TestLoader().loadTestsFromTestCase(TestSerialLiveMode),
        unittest.TestLoader().loadTestsFromTestCase(TestSocketLiveMode)
    ])).wasSuccessful()

    if not successful:
        sys.exit(1)
    else:
        sys.exit(0)
