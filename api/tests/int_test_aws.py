import unittest
from api.tests.setup import AWSSetupLayer
from api.tests.test_aws import AWSTestMixin
from manage.dynamo import DynamoDB


class IntTestAWStory(AWSTestMixin, unittest.TestCase):
    layer = AWSSetupLayer
    setup_helper = layer.setup_helper

    def setUp(self):
        """ Set everything up for testing """
        #cls.setup_helper = cls.layer.setup_helper
        DynamoDB.STACK_NAME = "int-{}".format(self.setup_helper.stack_name)
