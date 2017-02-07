# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pkg_resources import resource_filename

from moto import mock_dynamodb2
import os
import arrow

from manage.dynamo import DynamoDB
from api.aws import DynamoTable


class SetupTests(object):
    """ Class to handle setting up tests, including support for mocking

    """
    def __init__(self):
        self.mock = True
        self.mock_dynamodb = None
        self.table_list = ["campaigns.json",
                           "donations.json"]
        self.config_dir = resource_filename("manage", "configs")

        # Load test config
        self.stack_name = os.environ["STACK_NAME"]

    def start_mocking(self):
        """Method to start mocking"""
        self.mock = True
        self.mock_dynamodb = mock_dynamodb2()
        self.mock_dynamodb.start()

    def stop_mocking(self):
        """Method to stop mocking"""
        self.mock_dynamodb.stop()

    def _create_tables(self):
        """Method to create the S3 index table"""

        print("\n ** Creating DynamoDB Tables")

        # Create Tables
        for table_config in self.table_list:
            with open(os.path.join(self.config_dir, table_config), "rt") as handle:
                config_data = json.load(handle)
                story_table = DynamoDB(DynamoTable.STACK_NAME, config_data[self.stack_name])
                story_table.create()

    def create_tables(self):
        """Method to create DynamoDB tables"""
        if self.mock:
            mock_dynamodb2(self._create_tables())
        else:
            self._create_tables()

    def _delete_tables(self):
        """Method to delete table"""
        print("\n ** Deleting DynamoDB Tables")
        # Delete Story Table
        for table_config in self.table_list:
            with open(os.path.join(self.config_dir, table_config), "rt") as handle:
                config_data = json.load(handle)
                story_table = DynamoDB(DynamoTable.STACK_NAME, config_data[self.stack_name])
                story_table.delete()

    def delete_tables(self):
        """Method to create the tables"""
        if self.mock:
            mock_dynamodb2(self._delete_tables())
        else:
            self._delete_tables()


class AWSSetupLayer(object):
    """A nose2 layer for setting up temporary AWS resources for testing ONCE per run when doing integration tests"""
    DynamoTable.STACK_NAME = "int-{}".format(DynamoTable.STACK_NAME)
    setup_helper = SetupTests()

    @classmethod
    def setUp(cls):
        # setup resources
        cls.setup_helper.mock = False

        # Create AWS Resources needed for tests
        try:
            cls.setup_helper.create_tables()
        except Exception as err:
            print("An error occurred while creating integration test tables. Deleting Tables. Try again. {}".format(err))
            cls.setup_helper.delete_tables()

    @classmethod
    def tearDown(cls):
        # Delete tables
        cls.setup_helper.delete_tables()
