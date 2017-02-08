import unittest
from api.api_main import api
import json

from api.charity import SUPPORTED_CHARITIES


class APICharitiesTestMixin(object):

    def test_get(self):
        """Method to test post"""
        rv = self.app.get('/charities', follow_redirects=True)

        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)
        self.assertEqual(response, SUPPORTED_CHARITIES)


class TestAPICampaign(APICharitiesTestMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set everything up for testing """
        cls.app = api.app.test_client()

