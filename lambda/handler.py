import json

from api.campaign import SUPPORTED_CHARITIES


def store_donation(data):
    """Function to store the parsed donation record

    Args:
        data(dict):

    Returns:
        None
    """
    raise NotImplemented


def process_email_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Will process email here...")


