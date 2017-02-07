import boto3
import os
from pkg_resources import resource_filename
import json
import time
import sys


class DynamoDB(object):
    """Class to manage dynamodb tables"""

    def __init__(self, stack, config, aws_credentials):
        self.config = config
        self.aws_credentials = aws_credentials

        # Setup boto3
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        self.client = boto3.client('dynamodb', region_name="us-east-1")
        self.name = '{}.{}.wtt'.format(stack, config["TABLE_NAME"])
        self.table = None

    def exists(self):
        """Method to check if a table already exists

        Returns:
            (bool)
        """
        val = True
        try:
            _ = self.client.describe_table(TableName=self.name)
        except Exception as err:
            val = False
        return val

    def create(self):
        """Method to populate a dynamoDB config template and create the table

        Args:
            config(dict): Dictionary containing

        Returns:
            None
        """
        # Load template
        with open(os.path.join(resource_filename("manage", self.config["template"])), 'rt') as cf_handle:
            cf = cf_handle.read()

        # Replace variables
        for var in self.config:
            if var == "template":
                continue

            cf = cf.replace("<{}>".format(var), "{}".format(self.config[var]))

        # Make sure table doesn't already exist
        if self.exists():
            print("Table {} Already Exists. Cannot Create.".format(self.name))
            return

        # Create Table
        cf_dict = json.loads(cf)
        _ = self.client.create_table(TableName=self.name, **cf_dict)

        self.table = self.dynamodb.Table(self.name)

        # Wait for creation
        sys.stdout.write('Creating Table {}...'.format(self.name))
        sys.stdout.flush()
        while True:
            if self.client.describe_table(TableName=self.name)['Table']['TableStatus'] != u"ACTIVE":
                sys.stdout.write('.'.format(self.name))
                sys.stdout.flush()
                time.sleep(2)
            else:
                break
        sys.stdout.write('Done\n'.format(self.name))
        sys.stdout.flush()

    def delete(self):
        """Method to delete a table

        Returns:
            None
        """
        # Make sure table exists
        if not self.exists():
            print("Table {} does not exist. Nothing to Delete.".format(self.name))
            return

        # Delete table
        _ = self.client.delete_table(TableName=self.name)

        # Wait for deletion
        sys.stdout.write('Deleting Table {}...'.format(self.name))
        sys.stdout.flush()
        while self.exists():
            sys.stdout.write('.'.format(self.name))
            sys.stdout.flush()
            time.sleep(2)

        sys.stdout.write('Done\n'.format(self.name))
        sys.stdout.flush()
