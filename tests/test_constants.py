# -*- coding: UTF-8 -*-
"""Unit tests for the constants.py module"""
import unittest
import os
import ssl

from vlab_api_gateway import constants


class TestGetSSLContext(unittest.TestCase):
    """A suite of test cases for the ``_get_ssl_context`` function"""

    @classmethod
    def tearDown(cls):
        """Runs after every test case"""
        os.environ.pop('PRODUCTION', None)

    def test_not_production(self):
        """``_get_ssl_context`` doesn't verify TLS certs when not in production"""
        os.environ['PRODUCTION'] = 'false'
        context = constants._get_ssl_context()

        self.assertEqual(context.verify_mode, ssl.CERT_NONE)

    def test_in_production(self):
        """``_get_ssl_context`` verifies TLS certs when in production"""
        os.environ['PRODUCTION'] = 'true'
        context = constants._get_ssl_context()

        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)


class TestConst(unittest.TestCase):
    """A suite of test cases for the ``const`` attribute"""

    def test_keys(self):
        """``const`` has the expected number of defined constants"""
        found = [x for x in dir(constants.const) if x.startswith('VLAB')]
        expected = ['VLAB_FQDN', 'VLAB_SSL_CONTEXT']

        # set() so ordering doesn't cause false faliures
        self.assertEqual(set(found), set(expected))


if __name__ == '__main__':
    unittest.main()
