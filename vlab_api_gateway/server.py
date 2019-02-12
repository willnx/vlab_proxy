# -*- coding: UTF-8 -*-
"""This module glues together the downstream webserver (and client) with the
upstream back-end service"""
from gevent.pywsgi import WSGIServer
from http.client import HTTPConnection

from vlab_api_gateway import router
from vlab_api_gateway.relay import RelayQuery


def application(env, start_response):
    """The callable function per the WSGI spec; PEP 333"""
    headers = {x[5:].replace('_', '-'):y for x, y in env.items() if x.startswith('HTTP_')}
    headers['Content-Type'] = env.get('CONTENT_TYPE', '')
    headers['Content-Length'] = env.get('CONTENT_LENGTH', '')
    headers.pop('CONNECTION', None) # let RelayQuery choose to use keepalives or not
    body = env['wsgi.input']
    uri = env.get('PATH_INFO', '')
    if not uri:
        # Some WSGI servers use RAW_URI instead of PATH_INFO.
        # Gunicorn uses PATH_INFO, gevent.pywsgi.WSGIServer uses RAW_URI
        uri=env.get('RAW_URI', '')
    token = env.get('X-Auth', None)
    host, tls, port = router.get_host(uri=uri, token=token)
    host='137.69.150.53' # TODO - Delete this; it's a shim for local dev testing
    resp = RelayQuery(host=host,
                      method=env['REQUEST_METHOD'],
                      uri=uri,
                      headers=headers,
                      body=body,
                      port='5000',
                      tls=tls)
    start_response(resp.status, resp.headers)
    return resp


if __name__ == '__main__':
    print("Starting server")
    WSGIServer(('0.0.0.0', 8000), application).serve_forever()
