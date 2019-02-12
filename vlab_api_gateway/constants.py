# -*- coding: UTF-8 -*-
"""Defines all the run-time constant values"""
import ssl
from os import environ
from collections import namedtuple, OrderedDict


def _get_ssl_context():
    """Enables use of self-signed TLS certs for non-production uses"""
    production = environ.get('PRODUCTION', '').lower()
    if production != 'true':
        context = ssl.SSLContext()
        context.verify_mode = ssl.CERT_NONE
    else:
        context = ssl.create_default_context()
    return context


DEFINED = OrderedDict([
            ('VLAB_FQDN', environ.get('VLAB_FQDN', 'vlab.local')),
            ('VLAB_SSL_CONTEXT', _get_ssl_context()),
          ])

Constants = namedtuple('Constants', list(DEFINED.keys()))

# The '*' expands the list, just liked passing a function *args
const = Constants(*list(DEFINED.values()))
