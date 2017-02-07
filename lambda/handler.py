import json


def process_email_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Will process email here...")

