import boto3
import glob
import os


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
        s3.buckets(self.bucket_name).objects.delete()

        self.client.delete_bucket(Bucket=self.bucket_name)

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
        for filename in files:
            with open(filename, 'rb') as fh:
                bucket.upload_fileobj(fh, os.path.basename(filename))
