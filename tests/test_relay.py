# -*- coding: UTF-8 -*-
"""A suite of unit tests for the ``relay.py`` module"""
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from socket import gaierror

from vlab_api_gateway import relay

relay.logger = MagicMock() # prevent SPAM in output while running tests


class TestRelay(unittest.TestCase):
    """A suite of test cases for the ``relay.py`` module"""

    def test_no_host_404(self):
        """When host is None, an HTTP 404 is returned"""
        resp = relay.RelayQuery(host=None,
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)
        expected = '404 Not Found'
        actual = resp.status
        self.assertEqual(expected, actual)

    def test_no_host_error(self):
        """When host is None, the error message provides context"""
        resp = relay.RelayQuery(host=None,
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)
        expected = b'{"error": "unable to find host None for /foo"}'
        actual = b''.join(list(resp))
        self.assertEqual(expected, actual)

    @patch.object(relay, 'HTTPConnection')
    def test_happy_path(self, fake_HTTPConnection):
        """The Relay object transparently proxies the API request/response"""
        fake_resp = MagicMock()
        fake_resp.getheaders.return_value = {'FooHeader' : 'true'}
        fake_conn = MagicMock()
        fake_conn.getresponse.return_value = fake_resp
        fake_HTTPConnection.return_value = fake_conn

        resp = relay.RelayQuery(host='fooHost',
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)
        expected_headers = {'FooHeader' : 'true'}

        self.assertEqual(resp.headers, expected_headers)

    @patch.object(relay, 'HTTPSConnection')
    def test_https(self, fake_HTTPSConnection):
        """The Relay object can proxy to HTTPS services"""
        fake_resp = MagicMock()
        fake_resp.getheaders.return_value = {'FooHeader' : 'true'}
        fake_conn = MagicMock()
        fake_conn.getresponse.return_value = fake_resp
        fake_HTTPSConnection.return_value = fake_conn

        resp = relay.RelayQuery(host='fooHost',
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=443,
                                tls=True)
        expected_headers = {'FooHeader' : 'true'}

        self.assertEqual(resp.headers, expected_headers)

    @patch.object(relay, 'HTTPConnection')
    def test_resp_close(self, fake_HTTPConnection):
        """
        The Relay object has the ``close`` attribute, and calling it closes the
        socket to the backend service
        """
        fake_resp = MagicMock()
        fake_resp.getheaders.return_value = {'FooHeader' : 'true'}
        fake_conn = MagicMock()
        fake_conn.getresponse.return_value = fake_resp
        fake_HTTPConnection.return_value = fake_conn

        resp = relay.RelayQuery(host='fooHost',
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)
        resp.close()

        self.assertTrue(fake_conn.close.called)

    @patch.object(relay, 'HTTPConnection')
    def test_dns_failure(self, fake_HTTPConnection):
        """Failure to resolve the Host DNS name returns a NoHostResponse response"""
        fake_resp = MagicMock()
        fake_resp.getheaders.return_value = {'FooHeader' : 'true'}
        fake_conn = MagicMock()
        fake_conn.getresponse.return_value = fake_resp
        fake_conn.request.side_effect = [gaierror('testing')]
        fake_HTTPConnection.return_value = fake_conn

        resp = relay.RelayQuery(host='fooHost',
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)

        self.assertTrue(isinstance(resp._resp, relay.NoHostResponse))

    def test_headers(self):
        """A NoHostResponse returns the headers as a list of tuples"""
        resp = relay.RelayQuery(host=None,
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)
        expected = [('Content-Type', 'application/json')]
        actual = resp.headers
        self.assertEqual(expected, actual)

    @patch.object(relay, 'HTTPConnection')
    def test_connection_refused(self, fake_HTTPConnection):
        """Connection Refused by upstream hosts returns a NoHostResponse response"""
        fake_resp = MagicMock()
        fake_resp.getheaders.return_value = {'FooHeader' : 'true'}
        fake_conn = MagicMock()
        fake_conn.getresponse.return_value = fake_resp
        fake_conn.request.side_effect = [ConnectionRefusedError('testing')]
        fake_HTTPConnection.return_value = fake_conn

        resp = relay.RelayQuery(host='fooHost',
                                uri='/foo',
                                method='GET',
                                headers={},
                                body=StringIO('{}'),
                                port=5000)

        self.assertTrue(isinstance(resp._resp, relay.NoHostResponse))


if __name__ == '__main__':
    unittest.main()
