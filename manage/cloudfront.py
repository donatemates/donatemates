import boto3
import botocore
from botocore.exceptions import ClientError
from pkg_resources import resource_filename
import json
import os
import zipfile
import tempfile


from .util import get_account_id


class CloudFront(object):
    """Class to manage a cloudfront config"""

    def __init__(self, stack_name):
        """Constructor

        Args:
            stack_name(str): Name of the stack you are building

        Returns:
            None
        """
        self.cloudfront_client = boto3.client('cloudfront', region_name="us-east-1")
        self.lambda_client = boto3.client('lambda', region_name="us-east-1")
        self.lambda_func_name = '{}:donatemates-url-rewrite-{}'.format(get_account_id(), stack_name)
        self.stack_name = stack_name

    def get_code(self):
        """Zip up the code and return bytes

        Returns:
            bytes
        """
        with open(tempfile.NamedTemporaryFile().name, 'w') as zf:
            zfh = zipfile.ZipFile(zf.name, mode='w')

            old_path = os.getcwd()
            os.chdir(os.path.join(resource_filename("manage", "configs")))

            zfh.write("url_rewrite.js")
            zfh.close()
            zf.close()

            os.chdir(old_path)
            with open(zf.name, "rb") as zfr:
                return zfr.read()

    def assign_rewrite_lambda(self):
        """Method to create a role for a stack

        Returns:
            None
        """
        # Check if lambda function exists
        try:
            # Update Function
            response = self.lambda_client.update_function_code(FunctionName=self.lambda_func_name,
                                                               ZipFile=self.get_code())

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise Exception("Failed to update lambda@edge function! {}".format(response))

        except ClientError:
            # Assume it doesn't exist - create
            raise Exception("Only updating the re-write lambda is supported. Currently you must create the re-write lambda function manually first. Check out the readme")
            #response = self.lambda_client.create_function(FunctionName=self.lambda_func_name,
            #                                              Runtime='nodejs4.3-edge',
            #                                              Role='string',###
            #                                              Handler='index.handler',
            #                                              Code={
            #                                                  'ZipFile': b'bytes'###
            #                                              },
            #                           Description='Lambda@Edge url re-writes for stack: {}'.format(self.stack_name))
            #lambda_arn = None

            # Attach to CF distribution

        print("   ** Done!")



