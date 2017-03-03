import boto3
import botocore
from pkg_resources import resource_filename
import json
import os


class IAM(object):
    """Class to manage IAM roles for a stack"""

    def __init__(self, stack_name):
        """Constructor

        Args:
            stack_name(str): Name of the stack you are building

        Returns:
            None
        """
        self.client = boto3.client('iam', region_name="us-east-1")
        self.role_name = '{}-lambda-execution-role'.format(stack_name)
        self.policy_name = '{}-api-lambda-permissions'.format(stack_name)

    def create_role(self):
        """Method to create a role for a stack

        Returns:
            None
        """
        with open(os.path.join(resource_filename("manage", "configs"), "attach_policy.json"), 'rt') as policy:
            attach_policy = json.load(policy)
        with open(os.path.join(resource_filename("manage", "configs"), "assume_policy.json"), 'rt') as policy:
            assume_policy = json.load(policy)

        # Create the role if needed
        try:
            response = self.client.create_role(RoleName=self.role_name,
                                               AssumeRolePolicyDocument=json.dumps(assume_policy,
                                                                                   sort_keys=True,
                                                                                   indent=2))
        except botocore.exceptions.ClientError as e:
            # Assume a client error is a NoSuchEntity
            print("   Role exists. Deleting and re-creating")
            self.delete_role()
            response = self.client.create_role(RoleName=self.role_name,
                                               AssumeRolePolicyDocument=json.dumps(assume_policy,
                                                                                   sort_keys=True,
                                                                                   indent=2))

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("Failed to create Role.")

        response = self.client.put_role_policy(RoleName=self.role_name,
                                               PolicyName=self.policy_name,
                                               PolicyDocument=json.dumps(attach_policy, sort_keys=True, indent=2))

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("Failed to attached policy to bucket.")

    def delete_role(self):
        """Method to delete a role for a stack

        Returns:
            None
        """
        # Remove Role in-line policy
        try:
            iam = boto3.resource('iam')
            role_policy = iam.RolePolicy(self.role_name, self.policy_name)
            role_policy.delete()
        except botocore.exceptions.ClientError as e:
            # Assume a client error is a NoSuchEntity
            print("   No Role found. Skipping")
            return

        # Remove Role
        response = self.client.delete_role(RoleName=self.role_name)

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("Failed to delete policy.")
