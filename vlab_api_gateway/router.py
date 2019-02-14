# -*- coding: UTF-8 -*-
"""Contains business logic for proxying requests to correct back-end host"""
import base64

import ujson

from vlab_api_gateway.std_logger import get_logger
from vlab_api_gateway.constants import const

logger = get_logger(__name__)

SERVICE_MAP = {
# API Resource : (API Host, TLS, Port)
    'auth'       : ('auth-api', False, 5000),
    'link'       : ('link-api', False, 5000),
    'vlan'       : ('vlan-api', False, 5000),
    'gateway'    : ('gateway-api', False, 5000),
    'power'      : ('power-api', False, 5000),
    'inventory'  : ('inventory-api', False, 5000),
    'onefs'      : ('onefs-api', False, 5000),
    'insightiq'  : ('insightiq-api', False, 5000),
    'esrs'       : ('esrs-api', False, 5000),
    'cee'        : ('cee-api', False, 5000),
    'router'     : ('router-api', False, 5000),
    'windows'    : ('windows-api', False, 5000),
    'winserver'  : ('winserver-api', False, 5000),
    'centos'     : ('centos-api', False, 5000),
    'icap'       : ('icap-api', False, 5000),
    'claritynow' : ('claritynow-api', False, 5000),
    'ipam'       : ('UNKNOWN', True, 443),
    'docs'       : ('docs', False, 80),
}
SERVICE = 3
SERVICE_SUBGROUP = 4
NO_RECORD = (None, False, 0)


def get_host(uri, token):
    """Obtain the correct backend service to route the incoming request to

    :Returns: Tuple (host:str, tls:bool, port:int)

    :param uri: The API end point being called
    :type uri: String

    :param token: The auth token sent with the request
    :type token:
    """
    if not uri.startswith('/api'):
        host, tls, port = SERVICE_MAP.get('docs')
    else:
        uri_layers = uri.split('/')
        if uri_layers[SERVICE] == 'inf':
            host, tls, port = SERVICE_MAP.get(uri_layers[SERVICE_SUBGROUP], NO_RECORD)
        else:
            # services like "auth" and "link" are their own group; only 'inf' has subgroups
            host, tls, port = SERVICE_MAP.get(uri_layers[SERVICE], NO_RECORD)
            if host == 'UNKNOWN':
                host = _user_ipam_server(token)
    return host, tls, port


def _user_ipam_server(token):
    """Inspect the supplied auth token to determine the user's IPAM server

    :Returns: String or None

    :param token: The JWT supplied in the request
    :type token: Bytes
    """
    logger.info('Looking up IPAM server')
    try:
        header, payload, signature = token.split(b'.')
    except (ValueError, AttributeError, TypeError) as doh:
        # Mangled or missing JSON Web Token
        logger.exception(doh)
        user = None
    else:
        padding_needed = len(payload) % 4
        if padding_needed:
            payload += b'=' * (4 - padding_needed)
        decoded_payload = base64.urlsafe_b64decode(payload)
        try:
            username = ujson.loads(decoded_payload)['username']
            user = '{}.{}'.format(username, const.VLAB_FQDN)
        except ValueError:
            # bad json
            logger.error('invalid JSON for token payload')
            user = None
    return user
