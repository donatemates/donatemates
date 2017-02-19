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

    def test_scan_table(self):
        """Method to test scanning a table"""

        def scan_func(items, input_val):
            for item in items:
                if item["campaign_status"]["S"] == "complete":
                    input_val['count'] += 1
            return input_val

        campaign_table = DynamoTable('campaigns')

        # Add a record
        for idx in range(0, 10):
            data = {"campaign_id": "my_campaign_{}".format(idx),
                    "notified_on": arrow.utcnow().isoformat(),
                    "campaign_status": "complete"
                    }
            campaign_table.put_item(data)

        # Scan table
        result = {"count": 0}
        campaign_table.scan_table(scan_func, result, "campaign_status")

        self.assertEqual(result["count"], 10)


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
