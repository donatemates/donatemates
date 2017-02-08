import unittest
from api.tests.setup import AWSSetupLayer
from api.tests.test_api_charities import APICharitiesTestMixin
from api.api_main import api


class IntTestAPIStory(APICharitiesTestMixin, unittest.TestCase):
    layer = AWSSetupLayer
    setup_helper = layer.setup_helper
    app = api.app.test_client()
