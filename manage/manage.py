from pkg_resources import resource_filename
from .dynamo import DynamoDB
from .s3 import S3Bucket
from .iam import IAM
from api.aws import DynamoTable
import json
import boto3

import os
import shlex
from subprocess import Popen, PIPE
from .util import get_current_venv


def execute_in_virtualenv(virtualenv, commands):
    '''Execute Python code in a virtualenv, return its stdout and stderr.'''
    command_template = '/bin/bash -c "source {}/bin/activate && {}"'
    command = shlex.split(command_template.format(virtualenv, commands))
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    return process.communicate()


def populate_table(table, data_file, print_msg):
    """Method to populate a table with records stored in a dict loaded from a json file

    Args:
        table(api.aws.DynamoTable): the table to write to
        data_json(dict): the data to write. Should be an array in an object named 'data'

    Returns:
        None
    """
    with open(os.path.join(resource_filename("manage", "data"), data_file), 'rt') as df:
        data = json.load(df)
        if len(data["data"]) == 1:
            # Assume this is a campaign file for now.
            print(" - Example campaign loaded: https://<your_stack>/campaign.html?id={}".format(data["data"][0]["campaign_id"]))
        for item in data["data"]:
            table.put_item(item)
            print(print_msg)


class StackManager(object):
    """Class to manage an app stack deployment"""

    def __init__(self, stack_name):
        self.stack_name = stack_name
        self.config_dir = resource_filename("manage", "configs")
        self.root_dir = self.config_dir.rsplit('/', 2)[0]
        self.table_list = ["campaigns.json",
                           "donations.json"]

    def get_zappa_config(self):
        """Method to get a complete zappa config if a config is extended

        Returns:
            (str, dict): The package root and complete zappa config
        """
        # TODO: should do path lookup or config loading in a less brittle manner
        root_path = os.path.dirname(__file__).rsplit('/', 1)[0]
        with open(os.path.join(root_path, "zappa_settings.json"), "rt") as zh:
            zappa_config_all = json.load(zh)

        if "extends" in zappa_config_all[self.stack_name]:
            # Merge configs
            zappa_config = {}
            extends_config_name = zappa_config_all[self.stack_name]["extends"]
            for key in zappa_config_all[extends_config_name]:
                zappa_config[key] = zappa_config_all[extends_config_name][key]

            for key in zappa_config_all[self.stack_name]:
                zappa_config[key] = zappa_config_all[self.stack_name][key]

        else:
            zappa_config = zappa_config_all[self.stack_name]

        return root_path, zappa_config

    def create(self):
        """Method to create a stack

        Returns:
            None
        """
        print("\n ** Creating DynamoDB Tables")

        # Create Tables
        for table_config in self.table_list:
            with open(os.path.join(self.config_dir, table_config), "rt") as handle:
                config_data = json.load(handle)
                temp_table = DynamoDB(self.stack_name, config_data[self.stack_name])
                temp_table.create()

        # Create bucket for emails
        print("\n ** Creating email bucket: email-{}-donatemates".format(self.stack_name))
        email_bucket = S3Bucket('email-{}-donatemates'.format(self.stack_name))
        if not email_bucket.exists():
            email_bucket.create()
            print("Done.")
        else:
            print("Bucket Already Exists...skipping")

        print("\n ** Attaching S3 policy for SES ")
        email_bucket.attach_ses_policy(self.stack_name)

        print("\n ** Creating IAM role")
        role = IAM(self.stack_name)
        role.create_role()

        # Deploy API
        # Make sure stack doesn't already exist - Kind of kludgy right now
        print("\n ** Deploying API Stack {} (This may take 1-2 min)".format(self.stack_name))
        stack_exists = False
        stdout, stderr = execute_in_virtualenv(get_current_venv(), "zappa status {}".format(self.stack_name))
        if stderr:
            if "have you deployed yet?" in stderr:
                # Doesn't exist so deploy.
                stdout, stderr = execute_in_virtualenv(get_current_venv(),
                                                       "zappa deploy {}".format(self.stack_name))
                if stdout:
                    print(stdout)
                else:
                    print("An error occurred during API Deployment")
                    print(stderr)

            else:
                stack_exists = True
        else:
            stack_exists = True

        if stack_exists:
            print("Stack '{}' already exists. Can't deploy API.".format(self.stack_name))

        # get zappa config
        root_path, zappa_config = self.get_zappa_config()

        if "domain" in zappa_config:
            print("\n ** Setting up domain and SSL certs")
            stdout, stderr = execute_in_virtualenv(get_current_venv(),
                                                   "zappa certify {}".format(self.stack_name))
            if stdout:
                print(stdout)
            else:
                print("An error occurred during API Deployment")
                print(stderr)

            # Manually set base path as zappa isn't doing this yet
            api_gateway = boto3.client('apigateway', region_name=zappa_config["aws_region"])

            # Get the API ID
            paginator = api_gateway.get_paginator('get_rest_apis')
            rest_api_id = ""
            for response in paginator.paginate():
                for item in response["items"]:
                    if "{}-{}".format(zappa_config["project_name"], self.stack_name) == item["name"]:
                        rest_api_id = item["id"]

            response = api_gateway.create_base_path_mapping(domainName=zappa_config["domain"],
                                                            restApiId=rest_api_id,
                                                            stage=self.stack_name)

            if response["ResponseMetadata"]["HTTPStatusCode"] != 201:
                raise Exception("Failed to set up domain mapping in API Gateway.")

        # Copy frontend to bucket
        print("\n ** Updating Frontend ".format(self.stack_name))
        self.update_frontend()

        print("\n\nCreate Complete!")

    def update(self):
        """Method to update a stack

        Returns:
            None
        """
        print("\n ** Updating Table Schema not currently supported...skipping")

        # Update API
        print("\n ** Updating API Stack {} (This may take 1 min)".format(self.stack_name))

        # Make sure stack exists - Kind of kludgy right now
        stdout, stderr = execute_in_virtualenv(get_current_venv(), "zappa status {}".format(self.stack_name))
        if stderr:
            if "have you deployed yet?" in stderr:
                # Doesn't exist so can't tear down
                print("Stack '{}' does not exists. Can't update API. Try 'create' first.".format(self.stack_name))
                return
            else:
                raise Exception("Unknown response from zappa on check for stack: {}".format(stderr))
        else:
            # Stack exists. Tear it down.
            stdout, stderr = execute_in_virtualenv(get_current_venv(),
                                                   "zappa update {}".format(self.stack_name))
            if "Your updated Zappa deployment is live!" in stdout:
                print(stdout)
            else:
                print("An error occurred during API Tear Down")
                print(stdout)
                print("Error Stream:")
                print(stderr)

        # Update the frontend
        self.update_frontend()

        print("\n\nUpdate Complete!")

    def update_frontend(self):
        """Method to update just the frontend

        Returns:
            None
        """
        # Update Frontend
        print("\n ** Updating Frontend {}".format(self.stack_name))

        # get zappa config
        print("\n ** Emptying Frontend Bucket Contents".format(self.stack_name))
        root_path, zappa_config = self.get_zappa_config()
        frontend_bucket = S3Bucket(zappa_config["frontend_bucket"])
        if frontend_bucket.exists():
            frontend_bucket.empty()

        # get zappa config
        root_path, zappa_config = self.get_zappa_config()

        print("\n ** Writing Frontend Bucket Contents".format(self.stack_name))
        # Write endpoint.js
        with open(os.path.join(root_path, 'frontend', 'endpoint.js'), 'wt') as endpoint_file:
            endpoint_file.write('var rootUrl = "https://{}/";'.format(zappa_config["domain"]))

        # Update pre-launched bucket
        frontend_bucket = S3Bucket(zappa_config["frontend_bucket"])
        frontend_bucket.copy_dir(os.path.join(root_path, 'frontend', 'dist'))

    def delete(self):
        """Method to delete a Stack

        Returns:
            None
        """
        print("\n ** Deleting DynamoDB Tables")
        # Delete Tables
        for table_config in self.table_list:
            with open(os.path.join(self.config_dir, table_config), "rt") as handle:
                config_data = json.load(handle)
                temp_table = DynamoDB(self.stack_name, config_data[self.stack_name])
                temp_table.delete()

        # Undeploy API
        print("\n ** Tearing Down API Stack {} (This may take 1-2 min)".format(self.stack_name))

        # Make sure stack exists - Kind of kludgy right now
        stdout, stderr = execute_in_virtualenv(get_current_venv(), "zappa status {}".format(self.stack_name))
        if stderr:
            if "have you deployed yet?" in stderr:
                # Doesn't exist so can't tear down
                print("Stack '{}' does not exists. Can't tear down API.".format(self.stack_name))
            else:
                raise Exception("Unknown response from zappa on check for stack: {}".format(stderr))
        else:
            # Stack exists. Tear it down.
            stdout, stderr = execute_in_virtualenv(get_current_venv(),
                                                   "zappa undeploy -y {}".format(self.stack_name))
            if not stderr:
                print(stdout)
            else:
                print("An error occurred during API Tear Down")
                print(stderr)

        # Remove bucket contents for static page
        # get zappa config
        print("\n ** Emptying Frontend Bucket".format(self.stack_name))
        root_path, zappa_config = self.get_zappa_config()
        frontend_bucket = S3Bucket(zappa_config["frontend_bucket"])
        if frontend_bucket.exists():
            frontend_bucket.empty()

        # Remove bucket contents for emails
        print("\n ** Emptying Email Bucket".format(self.stack_name))
        email_bucket = S3Bucket('email-{}-donatemates'.format(self.stack_name))
        if email_bucket.exists():
            email_bucket.empty()

        # Delete role
        print("\n ** Deleting IAM role")
        role = IAM(self.stack_name)
        role.delete_role()

        print("\n\nDelete Complete!")

    def populate(self):
        """Populate the DBs with data to init things.

        Args:

        Returns:
            None
        """
        # Populate campaigns table
        print("Adding data to campaigns table")
        table = DynamoTable('campaigns')
        populate_table(table, "campaigns.json", " - Campaign Added")

        # Populate donations table
        print("Adding data to donations table")
        table = DynamoTable('donations')
        populate_table(table, "donations.json", " - Donation Added")
