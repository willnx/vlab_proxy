# -*- coding: UTF-8 -*-
"""
This module contains logic for calling the back-end service, and supplying
a response to the calling WSGI application.
"""
from socket import gaierror
from http.client import HTTPConnection, HTTPSConnection

from vlab_api_gateway.std_logger import get_logger
from vlab_api_gateway.constants import const

logger = get_logger(__name__)


class RelayQuery:
    """Call the back-end service and send the response downstream to the client

    This object is a small wrapper around the stdlib http.client API. The major
    reason for wrapping that API is so we can ensure the TCP socket to the back-end
    service gets closed after responding to the down-stream client.

    :param host: The IP/FQDN/DNS shortname of the back-end service to call.
    :type host: String

    :param uri: The API end point to envoke on the back-end service.
    :type uri: String

    :param method: The HTTP method to envoke (i.e. GET, POST, etc...)
    :type method: String

    :param headers: The HTTP headers to send to the back-end service.
    :type headers: Dictionary

    :param body: The HTTP body to send to the back-end service
    :type body: Bytes

    :param tls: Set to True to use HTTPS, False for HTTP. Default False.
    :type tls: Boolean
    """
    def __init__(self, host, uri, method, headers, body, port, tls=False):
        self._conn = None
        self._resp = None
        self._headers = None
        self._status = None
        if host is None:
            logger.error('No host found for {} on {}'.format(method, uri))
            self._handle_no_host(host, uri)
        else:
            self._call_upstream(host, uri, method, headers, body, port, tls)

    def _call_upstream(self, host, uri, method, headers, body, port, tls):
        if tls:
            self._conn = HTTPSConnection(host=host, port=port, context=const.VLAB_SSL_CONTEXT)
        else:
            self._conn = HTTPConnection(host=host, port=port)
        try:
            self._conn.request(method=method, url=uri, body=body, headers=headers)
        except gaierror:
            logger.error('failed to resolve DNS host {} for URI {}'.format(host, uri))
            self._handle_no_host(host, uri)
        except ConnectionRefusedError:
            logger.error('Connection refused by host - URL {}:{}{}, TLS={}'.format(host, port, uri, tls))
            self._handle_no_host(host, uri)
        else:
            self._resp = self._conn.getresponse()
            self._headers = self._resp.getheaders()
            self._status =  '{} {}'.format(self._resp.status, self._resp.reason)

    def _handle_no_host(self, host, uri):
        self._headers = [('Content-Type', 'application/json')]
        self._status = '404 Not Found'
        self._resp = NoHostResponse(host, uri)

    @property
    def headers(self):
        return self._headers

    @property
    def status(self):
        return self._status

    def close(self):
        """The WSGI spec states that if the returned object contains a callable
        named ``close`` that the Web server must execute it.

        Failure to close the TCP socket with the back-end service will lead to
        the API gateway "leaking sockets." Eventually the OS will prevent us
        from opening any new sockets, and all traffic will grind to a halt.
        """
        if self._conn:
            # NoHostResponse leaves this as None
            self._conn.close()

    def __iter__(self):
        return self

    def __next__(self):
        data = self._resp.readline()
        if data:
            return data
        else:
            raise StopIteration


class NoHostResponse:
    """Mimics the http.client.HTTPResponse objects API so the ``RelayQuery`` object
    can simply call methods.


    :param host: The back-end service to query. Used to give error message context
    :type host: String

    :param uri: The API endpoint used in query. Used to give error message context.
    :type uri: String
    """

    def __init__(self, host, uri):
        message = '{"error": "unable to find host %s for %s"}' % (host, uri)
        self.message = message.encode()
        self.sent_msg = False

    def readline(self):
        """Returns the HTTP body content

        :Returns: String or None
        """
        if self.sent_msg is False:
            self.sent_msg = True
            return self.message
        else:
            return None
