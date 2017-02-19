from boto3.dynamodb.types import Decimal
import boto3


def clean_dynamo_response(data):
    """Method to convert dynamodb response types to something that is serializable by JSON

        Supports up to 1 nesting layer

    Args:
        data (dict): Input dictionary of data

    Returns:
        (dict)
    """
    for key in data:
        if type(data[key]) is dict:
            for secondary in data[key]:
                if type(data[key][secondary]) is Decimal:
                    data[key][secondary] = float(data[key][secondary])
        if type(data[key]) is Decimal:
                    data[key] = float(data[key])
    return data


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

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print("**** Failed to send email to: {} - Error: {}".format(to_address, response))