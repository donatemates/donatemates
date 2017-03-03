import json
import boto3
import botocore
import os
import arrow
import charity
import shortuuid
import logging

from api.campaign import SUPPORTED_CHARITIES
from api.aws import DynamoTable
from .email import DonatematesEmail


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

    if "Item" in response:
        return response["Item"]
    else:
        return None


def process_email_handler(event, context):
    logger = logging.getLogger("boto3")
    logger.setLevel(logging.WARN)

    print("Received event: " + json.dumps(event, indent=2))

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
            # Found the charity

            # Get campaign ID and campaign data
            campaign_id = charity_class.get_campaign_id()
            print("CAMPAIGN ID: {}".format(campaign_id))
            campaign_table = DynamoTable('campaigns')
            campaign_key = {"campaign_id": campaign_id}
            campaign = campaign_table.get_item(campaign_key)

            if not campaign:
                print("WARNING: **** CAMPAIGN DOES NOT EXIST ****")
                dm_email = DonatematesEmail(charity_class.from_email)
                dm_email.send_campaign_does_not_exist()
                return True

            # Setup email sender
            dm_email = DonatematesEmail(charity_class.from_email, campaign["campaigner_email"])

            # Get donation receipt
            data = charity_class.parse_email()
            data["receipt_id"] = data["receipt_id"].strip()

            # Validate this is a new donation
            donation_table = DynamoTable('donations')
            existing_receipts = donation_table.query_hash("receipt_id", data["receipt_id"],
                                                          index="ReceiptIndex", limit=10)
            if existing_receipts:
                # This receipt already exists!
                print("WARNING: **** Duplicate receipt detected - Campaign: {} - Receipt: {} - Bucket: {} - Key: {} ****".format(campaign_id, data["receipt_id"], bucket, key))
                # Notify user we didn't process it
                dm_email.send_duplicate_receipt(campaign_id, data["receipt_id"], key)
                return True

            # Add donation record
            data["campaign_id"] = campaign_id
            data["donation_on"] = arrow.utcnow().isoformat()
            data["email_bucket"] = bucket
            data["email_key"] = key
            print("DONATION DATA:")
            print(data)
            store_donation(data)

            # Get updated total donation
            donation_total_cents = donation_table.integer_sum_attribute("campaign_id", campaign_id, "donation_cents")

            # Notify the Donor
            if campaign["campaign_status"] == "cancelled":
                # If cancelled, only notify donor and let them know the campaign isn't going on.
                dm_email.send_campaign_cancelled()
            else:
                # Send standard confirmation to donor
                dm_email.send_donation_confirmation(data["donation_cents"])

            # Notify the campaigner if the campaign is active only
            if campaign["campaign_status"] == "active":
                # Update notification time (for future possible digest emails)
                campaign_table.update_attribute(campaign_key, "notified_on", arrow.utcnow().isoformat())

                if donation_total_cents >= campaign["match_cents"]:
                    # Update campaign status to "matched"
                    campaign_table.update_attribute(campaign_key, "campaign_status", "matched")

                    # Send campaign completion email!
                    dm_email.send_campaign_matched(data["donor_name"], data["donation_cents"],
                                                   donation_total_cents, campaign["match_cents"])
                else:
                    # Send normal update
                    dm_email.send_campaign_update(data["donor_name"], data["donation_cents"],
                                                  donation_total_cents, campaign["match_cents"])

            # Exit
            return True

    # If you get here, you didn't successfully parse the email or it was unsupported
    # Save email to error bucket
    s3.Object('parse-fail-donatemates', '{}'.format(shortuuid.uuid())).copy_from(CopySource='{}/{}'.format(bucket, key))

    # Reply to user
    print("WARNING: **** Failed to detect a supported charity - Email Key: {} ****".format(key))




