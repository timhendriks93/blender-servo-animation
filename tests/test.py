import unittest

if __name__ == '__main__':
    integration_suite = unittest.TestLoader().discover('tests/integration')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(integration_suite)
