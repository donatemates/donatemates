import unittest
from api.aws import DynamoTable
from api.tests.setup import SetupTests
import json
import arrow


class AWSTestMixin(object):

    def test_list_receipt(self):
        """Method to test receipt index"""
        donation_table = DynamoTable('donations')
        receipt_id = "asdf1234"

        existing_receipts = donation_table.query_hash("receipt_id", receipt_id,
                                                      index="ReceiptIndex", limit=10)
        assert not existing_receipts

        # Add a record
        data = {"campaign_id": "my_campaign",
                "donation_on": arrow.utcnow().isoformat(),
                "donator_name": "John Doeski",
                "donator_email": "jd@gmail.dom",
                "donation_cents": 1000,
                "receipt_id": receipt_id,
                "email_bucket": "my_bucket",
                "email_key": "key1"
                }
        donation_table.put_item(data)

        existing_receipts = donation_table.query_hash("receipt_id", receipt_id,
                                                      index="ReceiptIndex", limit=10)

        assert len(existing_receipts) == 1

    def test_list_unrelated_receipts(self):
        """Method to test receipt index"""
        donation_table = DynamoTable('donations')

        # Add a record
        data = {"campaign_id": "my_campaign",
                "donation_on": arrow.utcnow().isoformat(),
                "donator_name": "John Doeski",
                "donator_email": "jd@gmail.dom",
                "donation_cents": 1000,
                "receipt_id": "alsdf3234",
                "email_bucket": "my_bucket",
                "email_key": "key1"
                }
        donation_table.put_item(data)

        data["receipt_id"] = "adsfghdfg"
        donation_table.put_item(data)

        data["receipt_id"] = "hjydfgsdfg"
        donation_table.put_item(data)

        existing_receipts = donation_table.query_hash("receipt_id", "jfghghjf",
                                                      index="ReceiptIndex", limit=10)

        assert not existing_receipts

    def test_dup_receipts_different_campaigns(self):
        """Method to test receipt index"""
        donation_table = DynamoTable('donations')
        receipt_id = "1234asdf"

        existing_receipts = donation_table.query_hash("receipt_id", receipt_id,
                                                      index="ReceiptIndex", limit=10)
        assert not existing_receipts

        # Add a record
        data = {"campaign_id": "my_campaign",
                "donation_on": arrow.utcnow().isoformat(),
                "donator_name": "John Doeski",
                "donator_email": "jd@gmail.dom",
                "donation_cents": 1000,
                "receipt_id": receipt_id,
                "email_bucket": "my_bucket",
                "email_key": "key1"
                }
        donation_table.put_item(data)

        data["campaign_id"] = "my_campaign2"
        donation_table.put_item(data)

        existing_receipts = donation_table.query_hash("receipt_id", receipt_id,
                                                      index="ReceiptIndex", limit=10)

        self.assertEqual(len(existing_receipts), 2)

    def test_delete_item(self):
        """Method to test receipt index"""
        campaign_table = DynamoTable('campaigns')

        # Add a record
        data = {"campaign_id": "my_campaign",
                "notified_on": arrow.utcnow().isoformat(),
                "campaign_status": "active"
                }
        campaign_table.put_item(data)

        # Verify write
        key = {"campaign_id": "my_campaign"}
        item = campaign_table.get_item(key)
        assert item is not None
        self.assertEqual(item["campaign_status"], "active")

        # Delete
        campaign_table.delete_item(key)

        # Verify it deleted
        item = campaign_table.get_item(key)
        assert item is None



class TestAWS(AWSTestMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set everything up for testing """
        # setup resources
        cls.setup_helper = SetupTests()
        cls.setup_helper.mock = True

        # Create AWS Resources needed for tests
        cls.setup_helper.start_mocking()
        cls.setup_helper.create_tables()

