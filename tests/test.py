import unittest

if __name__ == '__main__':
    integration_suite = unittest.TestLoader().discover('tests/integration')

    with open('tests/results.txt', 'w', encoding="utf-8") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        runner.run(integration_suite)
