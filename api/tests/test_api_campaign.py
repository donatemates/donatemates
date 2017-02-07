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

    def test_get(self):
        """Method to test post"""
        data = {"charity_name": "aclu",
                "campaigner_name": "John Doeski",
                "campaigner_email": "johndoeski@gmail.com",
                "match_cents": 5000}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)

        self.assertEqual(rv.status_code, 201)
        response = json.loads(rv.data)
        campaign_id = response["campaign_id"]

        # Get item
        rv = self.app.get('/campaign/{}'.format(campaign_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)
        self.assertEqual(response["charity_name"], data["charity_name"])
        self.assertEqual(response["campaigner_name"], data["campaigner_name"])
        self.assertEqual(response["campaigner_email"], data["campaigner_email"])
        self.assertEqual(response["match_cents"], data["match_cents"])
        self.assertEqual(response["notified_on"], response["notified_on"])

    def test_complex_campaign(self):
        """Method to test a more complex campaign with donors"""
        data = {"charity_name": "aclu",
                "campaigner_name": "John Doeski2",
                "campaigner_email": "johndoeski2@gmail.com",
                "match_cents": 25000}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)

        self.assertEqual(rv.status_code, 201)
        response = json.loads(rv.data)
        campaign_id = response["campaign_id"]

        # Add some donors
        dontation_table = DynamoTable('donations')

        donations = []
        for x in range(0, 7):
            donation = {"campaign_id": campaign_id,
                        "donation_on": arrow.utcnow().isoformat(),
                        "donator_name": "Friend {}".format(x),
                        "donator_email": "friend{}@gmail.com".format(x),
                        "donation_cents": 5000 - (250 * x),
                        "email_object": "https://s3.aws.com/somghasd"}
            dontation_table.put_item(donation)
            donations.append(donation)
            time.sleep(1)

        # Get item
        rv = self.app.get('/campaign/{}'.format(campaign_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)
        self.assertEqual(response["charity_name"], data["charity_name"])
        self.assertEqual(response["campaigner_name"], data["campaigner_name"])
        self.assertEqual(response["campaigner_email"], data["campaigner_email"])
        self.assertEqual(response["match_cents"], data["match_cents"])
        self.assertEqual(response["notified_on"], response["notified_on"])

        for donor, x in zip(response["large_donors"], range(0, 5)):
            self.assertEqual(donor["donator_name"], "Friend {}".format(x))

        for donor, x in zip(response["recent_donors"], range(6, 1, -1)):
            self.assertEqual(donor["donator_name"], "Friend {}".format(x))


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

