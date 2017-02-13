import json
import boto3
import botocore
import os
import arrow
import charity

from api.campaign import SUPPORTED_CHARITIES


def store_donation(data):
    """
    Function to store the parsed donation record

    Args:
        data(dict): Dictionary of data to put into a donation record. Default attributes:

            {
              "campaign_id": "qjKKg5LipvXY4r7ASik8ES",
              "donation_on": "2017-02-06T05:30:13.485936+00:00",
              "donor_name": "Neil DeGrasse Tyson",
              "donor_email": "neil@gmail.com",
              "donation_cents": 20000,
              "email_key": "asdfdfg45ty3tadf"
              "email_bucket": "email-stack-donatemates"
            }

    Returns:
        None
    """
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('{}.donations.donatemates'.format(os.environ.get('STACK_NAME')))
    response = table.put_item(Item=data, ReturnValues='NONE',
                              ReturnConsumedCapacity='NONE', ReturnItemCollectionMetrics='NONE')

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Error writing item to table: {}".format(response['ResponseMetadata']))


def get_campaigner_email(campaign_id):
    """
    Function to get the campaigner's email from the campaign ID

    Args:
        campaign_id(str): The campaign ID

    Returns:
        (str)
    """
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('{}.campaigns.donatemates'.format(os.environ.get('STACK_NAME')))
    try:
        response = table.get_item(Key={"campaign_id": campaign_id}, ConsistentRead=True)
    except botocore.exceptions.ClientError as err:
        raise IOError("Error getting item: {}".format(err.message))

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise IOError("Error getting item: {}".format(response['ResponseMetadata']))

    if "Item" in response:
        return response["Item"]["campaigner_email"]
    else:
        return None


def send_email(to_address, subject, text_msg, html_msg):
    """
    Function to send an email from the default address

    Args:
        to_address(str): The email address to send to
        subject(str): The email message subject
        text_msg(str): The plain text email
        html_msg(str): The HTML formatted message

    Returns:
        None
    """
    client = boto3.client('ses')
    response = client.send_email(
        Source="hello@donatemates.com",
        Destination={'ToAddresses': [to_address]},
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': text_msg,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': html_msg,
                    'Charset': 'UTF-8'
                }
            }
        })
    print(response)


def process_email_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print(event)

    # Check if S3 event or CloudWatch invocation. If just keeping things hot, exit.
    if "Records" in event:
        if "s3" in event["Records"][0]:
                key = event["Records"][0]["s3"]["object"]["key"]
                bucket = event["Records"][0]["s3"]["bucket"]["name"]
    else:
        print("Not an email")
        return

    # Load message from S3
    s3 = boto3.resource('s3')
    email_obj = s3.Object(bucket, key)
    email_mime = email_obj.get()['Body'].read().decode('utf-8')

    # Detect Charity
    for sup_charity in SUPPORTED_CHARITIES:
        class_ = getattr(charity, sup_charity["class"])
        charity_class = class_(email_mime)

        # Detect charity
        if charity_class.is_receipt():
            # Found the charity, parse
            data = charity_class.parse_email()

            # Get campaign ID
            campaign_id = charity_class.get_campaign_id()
            print("CAMPAIGN ID:")
            print(campaign_id)

            # Add donation record
            data["campaign_id"] = campaign_id
            data["donation_on"] = arrow.utcnow().isoformat()
            data["email_bucket"] = bucket
            data["email_key"] = key
            print("DONATION DATA:")
            print(data)
            store_donation(data)

            # Send confirmation to donator
            send_email(charity_class.from_email, "Donatemates Confirmation",
                       "This confirms your donation of {}. Thanks!".format(data["donation_cents"] / 100),
                       "This confirms your donation of {}. Thanks!".format(data["donation_cents"] / 100))

            # Send notification to campaigner
            campaigner_email = get_campaigner_email(campaign_id)
            print("CAMPAIGNER EMAIL: {}".format(campaigner_email))
            if campaigner_email:
                send_email(campaigner_email, "Donatemates: Campaign Update",
                           "This confirms your donation of ${}. Thanks!".format(data["donation_cents"] / 100),
                           "Someone just donated ${} to your campaign!".format(data["donation_cents"] / 100))
            else:
                print("**** Failed to get the campaigner's email ****")

            # Exit
            return True

    # If you get here, you didn't successfully parse the email or it was unsupported
    print("**** Failed to detect a supported charity ****")




