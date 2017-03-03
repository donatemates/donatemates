import boto3
import glob
import os
from tqdm import tqdm
from mimetypes import guess_type
from .util import get_account_id


class S3Bucket(object):
    """Class to manage S3 buckets"""

    def __init__(self, bucket_name):
        self.client = boto3.client('s3', region_name="us-east-1")
        self.bucket_name = bucket_name

    def exists(self):
        """Method to check if a bucket already exists

        Returns:
            (bool)
        """
        val = True
        try:
            _ = self.client.head_bucket(Bucket=self.bucket_name)
        except Exception as err:
            val = False
        return val

    def create(self):
        """Method to create a bucket

        Returns:
            (str): Location of the bucket
        """
        response = self.client.create_bucket(ACL='private', Bucket=self.bucket_name)

        return response["Location"]

    def delete(self):
        """Method to delete a bucket

        Returns:
            (None)
        """
        # Delete all items in the bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)

        self.empty()
        bucket.delete()

    def empty(self):
        """Method to empty a bucket - don't delete if you want to reuse this bucket later (so you don't lose it)

        Returns:
            (None)
        """
        # Delete all items in the bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)

        for key in bucket.objects.all():
            key.delete()

    def copy_dir(self, source_dir, subdir=None):
        """Method to copy a local directory to the bucket

        Returns:
            (None)
        """
        # Get list of files in dir
        if subdir:
            files = glob.glob(os.path.join(os.path.join(source_dir, subdir), "*"))
        else:
            files = glob.glob(os.path.join(source_dir, "*"))

        # upload files
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        if subdir:
            pbar = files
        else:
            pbar = tqdm(files)
            pbar.set_description("Copying Files")

        for filename in pbar:
            if os.path.isdir(filename):
                # Found a subdir, recurse
                if subdir:
                    self.copy_dir(source_dir, os.path.join(subdir, os.path.basename(filename)))
                    continue
                else:
                    self.copy_dir(source_dir, os.path.basename(filename))
                    continue

            mime_type = guess_type(filename)
            bucket.upload_file(filename, filename.split("{}/".format(source_dir))[1],
                               ExtraArgs={'ContentType': mime_type[0]})

    def attach_ses_policy(self, stack_name):
        """Method to attach a policy to a bucket to allow SES to write emails

        Args:
            policy:

        Returns:

        """
        # Get the account ID
        account_id = get_account_id()

        policy_str = """{
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Sid": "GiveSESPermissionToWriteEmail",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "ses.amazonaws.com"
                        ]
                    },
                    "Action": [
                        "s3:PutObject"
                    ],
                    "Resource": "arn:aws:s3:::$$$$$$/*",
                    "Condition": {
                        "StringEquals": {
                            "aws:Referer": "######"
                        }
                    }
                }
            ]
        }""".replace("$$$$$$", self.bucket_name).replace("######", account_id)

        s3 = boto3.resource('s3')
        bucket_policy = s3.BucketPolicy(self.bucket_name)
        response = bucket_policy.put(Policy=policy_str)

        if response["ResponseMetadata"]["HTTPStatusCode"] != 204:
            raise Exception("Failed to attached policy to bucket.")
