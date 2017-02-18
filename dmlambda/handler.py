import json
import boto3
import botocore
import os
import arrow
import charity
import shortuuid

from api.campaign import SUPPORTED_CHARITIES
from api.aws import DynamoTable


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
    # TODO: DMK cleanup to use DynamoTable class since importing now
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('{}.donations.donatemates'.format(os.environ.get('STACK_NAME')))
    response = table.put_item(Item=data, ReturnValues='NONE',
                              ReturnConsumedCapacity='NONE', ReturnItemCollectionMetrics='NONE')

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Error writing item to table: {}".format(response['ResponseMetadata']))


def get_campaign(campaign_id):
    """
    Function to get the campaign object from the campaign ID

    Args:
        campaign_id(str): The campaign ID

    Returns:
        data(dict): Dictionary of campaign record:

            {
              "charity_id": "aclu",
              "campaigner_name": "John Doeski",
              "campaigner_email": "johndoeski@gmail.com",
              "match_cents": 500000,
              "campaign_id": "qjKKg5LipvXY4r7ASik8ES",
              "campaign_status": "active",
              "notified_on": "2017-02-06T05:28:51.422919+00:00",
              "created_on": "2017-02-06T05:28:51.422919+00:00"
            }

    """
    # TODO: DMK cleanup to use DynamoTable class since importing now
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('{}.campaigns.donatemates'.format(os.environ.get('STACK_NAME')))
    try:
        response = table.get_item(Key={"campaign_id": campaign_id}, ConsistentRead=True)
    except botocore.exceptions.ClientError as err:
        raise IOError("Error getting item: {}".format(err.message))

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise IOError("Error getting item: {}".format(response['ResponseMetadata']))

    return response["Item"]


def send_email(to_address, subject, body):
    """
    Function to send an email from the default address

    Args:
        to_address(str): The email address to send to
        subject(str): The email message subject
        body(str): The email message body

    Returns:
        None
    """
    client = boto3.client('ses', region_name="us-east-1")
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
                    'Data': body,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body,
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
        print("Not an email. Move along...")
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
            data["receipt_id"] = data["receipt_id"].strip()

            # Validate this is a new donation
            donation_table = DynamoTable('donations')
            existing_receipts = donation_table.query_hash("receipt_id", data["receipt_id"],
                                                          index="ReceiptIndex", limit=10)
            # Get campaign ID
            campaign_id = charity_class.get_campaign_id()
            print("CAMPAIGN ID: {}".format(campaign_id))

            campaign = get_campaign(campaign_id)
            if not campaign:
                print("**** CAMPAIGN DOES NOT EXIST ****")
                email_msg = "Sorry, the campaign email address you used does not exist. Double check and forward your receipt again!"
                send_email(charity_class.from_email, "Donatemates: Campaign not found", email_msg)
                return True

            if existing_receipts:
                # This receipt already exists!
                print("**** Duplicate receipt detected - Campaign: {} - Receipt: {} - Bucket: {} - Key: {} ****".format(campaign_id, data["receipt_id"], bucket, key))
                # Notify user we didn't process it
                email_msg = "Sorry, we weren't able to process your donation as it looks like you've already submitted it to Donatemates for a match campaign."
                email_msg = "{} If you think this was an error, please forward this email to help@donatemates.com and we'll look into it. Thanks!".format(email_msg)
                email_msg = "{} \r\n \r\nrequest_id: {}/{}/{}".format(email_msg, campaign_id, data["receipt_id"], key)
                send_email(charity_class.from_email, "Donatemates: Unable to process donation", email_msg)
                return True

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
                       "Thank you for your donation of ${}. We've added it to the match campaign and have let the matcher know as well. Thank you!".format(data["donation_cents"] / 100))

            # Send notification to campaigner
            campaigner_email = campaign["campaigner_email"]

            # Get updated total donation
            donation_total_cents = donation_table.integer_sum_attribute("campaign_id", campaign_id, "donation_cents")

            print("CAMPAIGNER EMAIL: {}".format(campaigner_email))
            if campaigner_email:
                send_email(campaigner_email, "Donatemates: Campaign Update",
                           "Good news! {} just donated ${} to your campaign! You're at ${} out of the total ${} you've offered to match.".format(data["donor_name"], data["donation_cents"] / 100, donation_total_cents / 100, campaign["match_cents"] / 100))

                # Update campaigner notification time
            else:
                print("**** Failed to get the campaigner's email ****")

            # Exit
            return True

    # If you get here, you didn't successfully parse the email or it was unsupported
    # Save email to error bucket
    s3.Object('parse-fail-donatemates', '{}'.format(shortuuid.uuid())).copy_from(CopySource='{}/{}'.format(bucket, key))

    # Reply to user
    print("**** Failed to detect a supported charity ****")




