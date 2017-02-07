import unittest
from api.tests.setup import AWSSetupLayer
from api.tests.test_api_campaign import APICampaignTestMixin
from manage.dynamo import DynamoDB
from api.api_main import api


class IntTestAPIStory(APICampaignTestMixin, unittest.TestCase):
    layer = AWSSetupLayer
    setup_helper = layer.setup_helper
    app = api.app.test_client()

    def setUp(self):
        """ Set everything up for testing """
        #cls.setup_helper = cls.layer.setup_helper
        DynamoDB.STACK_NAME = "int-{}".format(self.setup_helper.stack_name)