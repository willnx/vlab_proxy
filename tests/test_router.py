# -*- UTF-8 -*-
"""Unit test for the router.py module"""
import unittest
from unittest.mock import MagicMock, patch
import base64
import json

from vlab_api_gateway import router
from vlab_api_gateway.constants import const

router.logger = MagicMock() # prevent spam output while running unittest


class TestGetHost(unittest.TestCase):
    """A suite of test cases for ``get_host`` function of the router.py module"""

    def test_docs(self):
        """``get_host`` defaults to the docs service if the requests isn't for an API endpoint"""
        result = router.get_host(uri='/asdfsdwe', token=b'asdf.asdf.asdf')
        expected = ('docs', False, 80)

        self.assertEqual(result, expected)

    def test_inf(self):
        """``get_host`` indexes into the URI to find inf sub-services"""
        result = router.get_host(uri='/api/2/inf/winserver', token=b'asdf.asdf.asdf')
        expected = ('winserver-api', False, 5000)

        self.assertEqual(result, expected)

    def test_not_inf(self):
        """``get_host`` finds the correct host with the URI isn't part of 'inf'"""
        result = result = router.get_host(uri='/api/2/auth/token', token=b'asdf.asdf.asdf')
        expected = ('auth-api', False, 5000)

        self.assertEqual(result, expected)

    def test_ipam(self):
        """``get_host`` handles finding the correct host for the IPAM service"""
        token_payload = base64.urlsafe_b64encode(json.dumps({'username' : 'sandy'}).encode())
        token = b'asdf.%s.asdf' % token_payload

        result = router.get_host(uri='/api/1/ipam/portmap', token=token)
        expected = ('sandy.{}'.format(const.VLAB_FQDN), True, 443)

        self.assertEqual(result, expected)


class TestIpam(unittest.TestCase):
    """A suite of test cases for the ``_user_ipam_server`` function"""

    def test_missing_token(self):
        """``_user_ipam_server`` supplying None for the param ``token`` returns None"""
        result = router._user_ipam_server(token=None)
        expected = None

        self.assertEqual(result, expected)

    def test_malformed_token(self):
        """``_user_ipam_server`` returns None if the JWT is malformed"""
        token = b'asdf' # should be 3 sections separated by a period; ex asdf.asdf.asdf
        result = router._user_ipam_server(token=token)
        expected = None

        self.assertEqual(result, expected)

    def test_token_not_bytes(self):
        """``_user_ipam_server`` returns None if the JWT not Bytes"""
        token = 'asdf.asdf.asdf'
        result = router._user_ipam_server(token=token)
        expected = None

        self.assertEqual(result, expected)

    @patch.object(router.base64, 'urlsafe_b64decode')
    def test_token_padding(self, fake_urlsafe_b64decode):
        """``_user_ipam_server`` adds padding as needed for urlsafe_b64decode of JWT"""
        json_data = json.dumps({'username' : 'sandy', 'extra_crap' : True}).encode()
        token_payload = base64.urlsafe_b64encode(json_data)
        unpadded_payload = token_payload.replace(b'=', b'') # = is the padding char for base64
        token = b'asdf.%s.asdf' % unpadded_payload
        fake_urlsafe_b64decode.return_value = json.dumps({'username' : 'sandy'})

        router._user_ipam_server(token=token)

        call_args, _ = fake_urlsafe_b64decode.call_args
        padded_token = call_args[0]

        self.assertNotEqual(padded_token, unpadded_payload)
        self.assertEqual(padded_token, token_payload)

    def test_invalid_json(self):
        """``_user_ipam_server`` returns None if it cannot deserialize the JSON token payload"""
        token = b'asdf.asdf.asdf'
        result = router._user_ipam_server(token=token)
        expected = None

        self.assertEqual(result, expected)

class TestConstants(unittest.TestCase):
    """a suite of test cases for the router module constants"""

    def test_known_hosts(self):
        """``SERVICE_MAP`` contains the expected set of service hosts"""
        known_hosts = set(router.SERVICE_MAP.keys())
        expected_hosts = set(['snapshot', 'icap', 'centos', 'claritynow',
                              'router', 'gateway', 'insightiq', 'power', 'docs',
                              'onefs', 'windows', 'link', 'ecs', 'esrs', 'ipam',
                              'vlan', 'auth', 'cee', 'inventory', 'winserver',
                              'esxi'])

        self.assertEqual(known_hosts, expected_hosts)

    def test_service_index(self):
        """``SERVICE`` is the expected index into the API namespace"""
        expected_index = 3

        self.assertEqual(router.SERVICE, expected_index)

    def test_service_subgroup_index(self):
        """``SERVICE_SUBGROUP`` is the expected index into the API namespace"""
        expected_index = 4

        self.assertEqual(router.SERVICE_SUBGROUP, expected_index)

    def test_no_record(self):
        """``NO_RECORD`` is the expected tuple"""
        expected_tuple = (None, False, 0)

        self.assertEqual(router.NO_RECORD, expected_tuple)



if __name__ == '__main__':
    unittest.main()
