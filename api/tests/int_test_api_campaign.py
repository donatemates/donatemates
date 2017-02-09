import unittest
from api.tests.setup import AWSSetupLayer
from api.tests.test_api_campaign import APICampaignTestMixin
from manage.dynamo import DynamoDB
from api.aws import DynamoTable
from api.api_main import api
import json
import time
import arrow
import os


class IntTestAPIStory(APICampaignTestMixin, unittest.TestCase):
    layer = AWSSetupLayer
    setup_helper = layer.setup_helper
    app = api.app.test_client()

    def setUp(self):
        """ Set everything up for testing """
        #cls.setup_helper = cls.layer.setup_helper
        DynamoDB.STACK_NAME = "int-{}".format(self.setup_helper.stack_name)

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
                "match_cents": 2500000}
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
                        "donation_cents": 400000 - (25000 * x),
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

        self.assertEqual(response["dontation_total_cents"], 2275000)

    @unittest.skipUnless(os.environ.get('RUN_SCALE_TESTS'), "Test requires production scale database")
    def test_large_campaign(self):
        """Method to test a more complex campaign with donors"""
        data = {"charity_name": "aclu",
                "campaigner_name": "John Doeski2",
                "campaigner_email": "johndoeski2@gmail.com",
                "match_cents": 2500000}
        rv = self.app.post('/campaign', data=data, follow_redirects=True)

        self.assertEqual(rv.status_code, 201)
        response = json.loads(rv.data)
        campaign_id = response["campaign_id"]

        # Add some donors
        dontation_table = DynamoTable('donations')

        with dontation_table.table.batch_writer() as batch:
            for x in range(0, 5000):
                donation = {"campaign_id": campaign_id,
                            "donation_on": arrow.utcnow().isoformat(),
                            "donator_name": "Friend {}".format(x),
                            "donator_email": "friend{}@gmail.com".format(x),
                            "donation_cents": 1000,
                            "email_object": "https://s3.aws.com/somghasd"}
                batch.put_item(Item=donation)

        # Get item
        start_time = time.time()
        rv = self.app.get('/campaign/{}'.format(campaign_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        response = json.loads(rv.data)
        self.assertEqual(response["charity_name"], data["charity_name"])
        self.assertEqual(response["campaigner_name"], data["campaigner_name"])
        self.assertEqual(response["campaigner_email"], data["campaigner_email"])
        self.assertEqual(response["match_cents"], data["match_cents"])
        self.assertEqual(response["notified_on"], response["notified_on"])

        self.assertEqual(response["dontation_total_cents"], 5000000)
        print("Query took {:0.5f}s".format((time.time() - start_time)))

