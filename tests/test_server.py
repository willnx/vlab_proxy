# -*- coding: UTF-8 -*-
"""Unit tests for the server.py module"""
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from collections.abc import Iterable

import vlab_api_gateway.server


@patch('vlab_api_gateway.server.RelayQuery')
class TestServer(unittest.TestCase):
    """A suite of test cases for the server.py module"""
    @classmethod
    def setUp(cls):
        """ Runs before every test case"""
        cls.env = {}
        cls.env['REQUEST_METHOD'] = 'GET'
        cls.env['wsgi.input'] = StringIO('{}')

    def test_start_response_params(self, fake_RelayQuery):
        """``application`` calls start_response with the correct PEP 333 params"""
        fake_start_response = MagicMock()
        fake_resp = MagicMock()
        fake_resp.status = '200 OK'
        fake_resp.headers = {}
        fake_RelayQuery.return_value = fake_resp

        vlab_api_gateway.server.application(self.env, fake_start_response)

        call_args, _ = fake_start_response.call_args
        expected = (fake_resp.status, fake_resp.headers)

        self.assertEqual(call_args, expected)

    def test_resp_iterable(self, fake_RelayQuery):
        """``application`` returns a response object that supports the iter protocol"""
        fake_start_response = MagicMock()

        resp = vlab_api_gateway.server.application(self.env, fake_start_response)

        self.assertTrue(isinstance(resp, Iterable))

    def test_resp_closeable(self, fake_RelayQuery):
        """``application`` returns a response object that can be closed"""
        fake_start_response = MagicMock()

        resp = vlab_api_gateway.server.application(self.env, fake_start_response)

        self.assertTrue(hasattr(resp, 'close'))

    def test_raw_uri(self, fake_RelayQuery):
        """``application`` supports use of the RAW_URI envvar for defining the API end point"""
        self.env['RAW_URI'] = '/woot'
        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        expected_uri = '/woot'

        self.assertEqual(called_kwargs['uri'], expected_uri)

    def test_pop_connection_header(self, fake_RelayQuery):
        """``application`` does not pass the Connection HTTP header to the proxying logic"""
        self.env['CONNECTION'] = 'keep-alive'
        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        proxied_headers = called_kwargs['headers']
        expected_headers = {'Content-Length': '', 'Content-Type': ''}

        self.assertEqual(proxied_headers, expected_headers)

    def test_extra_http_headers(self, fake_RelayQuery):
        """``application`` pass all extra HTTP headers to the proxing logic"""
        self.env['HTTP_X_CUSTOM_HEADER'] = 'woot'

        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        proxied_headers = called_kwargs['headers']
        expected_headers = {'Content-Length': '', 'Content-Type': '', 'X-CUSTOM-HEADER': 'woot'}

        self.assertEqual(proxied_headers, expected_headers)



if __name__ == '__main__':
    unittest.main()