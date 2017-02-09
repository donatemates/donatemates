import unittest
from api.tests.setup import SetupTests
from api.aws import DynamoTable
from api.api_main import api
import json
import arrow
import time


class APICampaignTestMixin(object):

    def test_post_missing_args(self):
        """Method to test when required args are missing"""
        data = {"charity": "aclu"}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_story_not_found(self):
        """Method to test posting with an ID"""
        rv = self.app.get('/campaign/adfhdf2354uhs')
        self.assertEqual(rv.status_code, 404)

    def test_post(self):
        """Method to test post"""
        data = {"charity_name": "aclu",
                "campaigner_name": "John Doeski",
                "campaigner_email": "johndoeski@gmail.com",
                "match_cents": 5000}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)

        self.assertEqual(rv.status_code, 201)
        response = json.loads(rv.data)
        assert "campaign_id" in response

    def test_post_bad_charity(self):
        """Method to test post"""
        data = {"charity_name": "aclusd",
                "campaigner_name": "John Doeski",
                "campaigner_email": "johndoeski@gmail.com",
                "match_cents": 5000}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)

        self.assertEqual(rv.status_code, 400)


class TestAPICampaign(APICampaignTestMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set everything up for testing """
        cls.app = api.app.test_client()

        # setup resources
        cls.setup_helper = SetupTests()
        cls.setup_helper.mock = True

        # Create AWS Resources needed for tests
        cls.setup_helper.start_mocking()
        cls.setup_helper.create_tables()

    @classmethod
    def tearDownClass(cls):
        # Delete tables
        cls.setup_helper.delete_tables()
        # Stop mocking
        cls.setup_helper.stop_mocking()

