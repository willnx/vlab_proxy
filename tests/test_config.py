# -*- coding: UTF-8 -*-
"""A suite of unit tests for the config.py module"""
import unittest

from vlab_api_gateway import config

class TestConfig(unittest.TestCase):
    """A suite of test cases for the ``config.py`` module"""

    def test_bind(self):
        """"``config`` sets the bind parameter to the expected value"""
        expected = '0.0.0.0'
        self.assertEqual(config.bind, expected)

    def test_worker_class(self):
        """``config`` sets the worker_class parameter to the expected value"""
        expected = 'gevent'
        self.assertEqual(config.worker_class, expected)

    def test_workers(self):
        """``config`` sets the workers parameter to the expected value"""
        expected = 1
        self.assertEqual(config.workers, expected)

    def test_name(self):
        """``config`` sets the name parameter to the expected value"""
        expected = 'vlab-api-gateway'
        self.assertEqual(config.name, expected)

    def test_number_of_parameters(self):
        """``config`` contains the expected number of defined parameters"""
        std_python_attrs = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__']

        defined_params = [x for x in dir(config) if x not in std_python_attrs]
        expected = ['bind', 'name', 'worker_class', 'workers']

        # set() prevents false positives due to ordering
        self.assertEqual(set(defined_params), set(expected))


if __name__ == '__main__':
    unittest.main()
