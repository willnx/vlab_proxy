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
        expected_headers = {}

        self.assertEqual(proxied_headers, expected_headers)

    def test_extra_http_headers(self, fake_RelayQuery):
        """``application`` pass all extra HTTP headers to the proxing logic"""
        self.env['HTTP_X_CUSTOM_HEADER'] = 'woot'

        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        proxied_headers = called_kwargs['headers']
        expected_headers = {'X-CUSTOM-HEADER': 'woot'}

        self.assertEqual(proxied_headers, expected_headers)

    def test_content_headers(self, fake_RelayQuery):
        """``application`` sends Content-Type and Content-Lenght headers when they exist"""
        self.env['CONTENT_TYPE'] = 'application/json'
        self.env['CONTENT_LENGTH'] = 50
        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        proxied_headers = called_kwargs['headers']
        expected_headers = {'Content-Type': 'application/json', 'Content-Length': 50}

        self.assertEqual(proxied_headers, expected_headers)

    @patch.object(vlab_api_gateway.server, 'router')
    def test_x_auth_header(self, fake_router, fake_RelayQuery):
        """``application`` pulls the JWT auth token and passes it as bytes"""
        self.env['HTTP_X_AUTH'] = 'asdf.asdf.asdf'
        fake_start_response = MagicMock()
        fake_router.get_host.return_value = ('someHost', False, 5000)

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, call_kwargs  = fake_router.get_host.call_args
        called_token = call_kwargs['token']

        self.assertEqual(called_token, self.env['HTTP_X_AUTH'].encode())

    def test_passes_port(self, fake_RelayQuery):
        """``application`` passes the correct port to RelayQuery"""
        self.env['PATH_INFO'] = '/'
        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        port_used = called_kwargs['port']
        port_expected = 80

        self.assertEqual(port_used, port_expected)

    def test_passes_query_params(self, fake_RelayQuery):
        """``application`` passes all query params that are supplied"""
        self.env['QUERY_STRING'] = 'foo=true'
        self.env['PATH_INFO'] = '/api/1/ipam'
        fake_start_response = MagicMock()

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, called_kwargs = fake_RelayQuery.call_args
        uri_used = called_kwargs['uri']
        uri_expected = '/api/1/ipam?foo=true'

        self.assertEqual(uri_used, uri_expected)

    @patch.object(vlab_api_gateway.server.router, 'get_host')
    def test_no_mangle_host(self, fake_get_host, fake_RelayQuery):
        """``application`` doesn't mangle how 'router' identifies a host"""
        self.env['QUERY_STRING'] = 'foo=true'
        self.env['PATH_INFO'] = '/api/1/ipam'
        fake_start_response = MagicMock()
        fake_get_host.return_value = (1,2,3)

        vlab_api_gateway.server.application(self.env, fake_start_response)

        _, the_kwargs = fake_get_host.call_args
        sent_uri = the_kwargs['uri']
        expected = '/api/1/ipam'

        self.assertEqual(sent_uri, expected)


if __name__ == '__main__':
    unittest.main()
