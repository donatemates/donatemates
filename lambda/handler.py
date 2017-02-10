import json
import charity
import boto3

from api.campaign import SUPPORTED_CHARITIES


def store_donation(data):
    """
    Function to store the parsed donation record

    Args:
        data(dict):

    Returns:
        None
    """
    raise NotImplementedError


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
    print("Will process email here...")
    send_email("dean.kleissas@gmail.com", "testingsend", "asdjlajsdfjlads", "asdf")
    return

    # Check if S3 event or CloudWatch invocation. If just keeping things hot, exit.

    # Get email object Key

    # Load message from S3 and key

    # Detect Charity
    charity_class = None
    for charity in SUPPORTED_CHARITIES:
        class_ = getattr(charity, SUPPORTED_CHARITIES[charity]["class"])
        charity_class = class_("email text here")

        # Detect charity
        if charity_class.is_receipt():
            # Found the charity, parse
            charity_class.parse_email()

            # Add donation record

            # Send confirmation to donator

            # Send notification to campaigner

            # Exit
            return True

    # If you get here, you didn't successfully parse the email or it was unsupported
    print("Failed to detect a supported charity")




