# pylint: disable=wrong-import-position

import unittest
import os
import pathlib
import sys

main_dir = pathlib.Path(os.path.dirname(__file__)).resolve()
sys.path.append(str(main_dir))

from export import TestExport
from serial_live_mode import TestSerialLiveMode
from socket_live_mode import TestSocketLiveMode

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(TestExport),
            unittest.TestLoader().loadTestsFromTestCase(TestSerialLiveMode),
            unittest.TestLoader().loadTestsFromTestCase(TestSocketLiveMode)
        ])
    )
