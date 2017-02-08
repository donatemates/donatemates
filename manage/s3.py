import boto3
import glob
import os
from tqdm import tqdm
from mimetypes import guess_type


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

    def copy_dir(self, source_dir):
        """Method to copy a local directory to the bucket

        Returns:
            (None)
        """
        # Get list of files in dir
        files = glob.glob(os.path.join(source_dir, "*"))

        # upload files
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        pbar = tqdm(files)
        pbar.set_description("Copying Files")
        for filename in pbar:
            mime_type = guess_type(filename)
            bucket.upload_file(filename, os.path.basename(filename), ExtraArgs={'ContentType': mime_type[0]})
