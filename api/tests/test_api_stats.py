import unittest
from api.tests.setup import SetupTests
from api.aws import DynamoTable
from api.api_main import api
import json
import arrow
import shortuuid


class APIStatsTestMixin(object):

    def test_stats(self):
        """Method to test stats routingt"""
        rv = self.app.get('/stats', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/stats/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

    def test_stats(self):
        """Method to test stats endpoint"""
        rv = self.app.get('/stats', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)
        self.assertEqual(response["campaign_count"], 0)
        self.assertEqual(response["donation_count"], 0)
        self.assertEqual(response["total_donation_cents"], 0)

        data = {"charity_id": "aclu",
                "campaigner_name": "John Doeski",
                "campaigner_email": "johndoeski@gmail.com",
                "match_cents": 5000}
        for idx in range(0, 15):
            rv = self.app.post('/campaign', data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 201)
        response = json.loads(rv.data)

        # Add some cancelled and matched campaignes
        campaign_table = DynamoTable('campaigns')

        for x in range(0, 4):
            camp = {"campaign_id": shortuuid.uuid(),
                    "notified_on": arrow.utcnow().isoformat(),
                    "campaign_status": "cancelled",
                    "match_cents": 20000}
            campaign_table.put_item(camp)

        for x in range(0, 2):
            camp = {"campaign_id": shortuuid.uuid(),
                    "notified_on": arrow.utcnow().isoformat(),
                    "campaign_status": "matched",
                    "match_cents": 20000}
            campaign_table.put_item(camp)

        # Add some donations
        dontation_table = DynamoTable('donations')
        donations = []
        for x in range(0, 7):
            donation = {"campaign_id": response["campaign_id"],
                        "donation_on": arrow.utcnow().isoformat(),
                        "donor_name": "Friend {}".format(x),
                        "donor_email": "friend{}@gmail.com".format(x),
                        "donation_cents": 20000}
            dontation_table.put_item(donation)
            donations.append(donation)

        rv = self.app.get('/stats', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)

        self.assertEqual(response["campaign_count"], 21)
        self.assertEqual(response["campaign_active_count"], 15)
        self.assertEqual(response["campaign_matched_count"], 2)
        self.assertEqual(response["campaign_cancelled_count"], 4)
        self.assertEqual(response["campaign_total_cents"], 115000)
        self.assertEqual(response["donation_count"], 7)
        self.assertEqual(response["total_donation_cents"], 140000)


class TestAPIStats(APIStatsTestMixin, unittest.TestCase):

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
        cls.setup_helper.setup_ses()

    @classmethod
    def tearDownClass(cls):
        # Delete tables
        cls.setup_helper.delete_tables()
        # Stop mocking
        cls.setup_helper.stop_mocking()

