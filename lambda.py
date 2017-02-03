from __future__ import print_function

import json
import urllib
import email
import boto3

"""
Messages in a dictionary form should adhere to the following spec:

{
    'from': str
    'to': str
    'amount': str, to accommodate different currencies or units
    'date': str right now... needs to be converted to millis, perhaps?
    'subject': str
    ...
}

Messages can hold any EXTRA fields, but most have at LEAST these fields.
For instance,

{
    'aclu_confirmation_code': '12345',
    'from': 'Donald Frump <thefrumpinator@yahoo.net>',
    'to': '"Kayley-anne Conrad's ACLU Campaign" <kayley-anne-conrad-a31c14e59deb@donatemates.com>',
    'amount': '$200.00', 'date': 'Thu, 01 Feb 2015 21:54:02 +0000',
    'subject': 'Fwd: Thank you for your gift to the ACLU'
}

is a valid dictionary.
"""

s3 = boto3.client('s3')

"""
Organization parsers
"""
def parse_email_aclu(msg):
    """
    Parses an ACLU donation email (NOT ACLU Foundation).

    Arguments:
        msg (email.Message): The message to parse. Generally a multipart MIME

    Returns:
        dict: See spec above.
    """
    out_msg = {}
    try:
        out_msg['from'] = msg["from"]
        out_msg['date'] = msg["date"]
        out_msg['to'] = msg["to"]
        out_msg['subject'] = msg["subject"]

        # Get the plaintext message:
        parts = [x for x in msg.get_payload()]
        text_msg_lines = parts[0].get_payload().split('\n')

        for i in range(len(text_msg_lines)):
            # We happen to know that the value of each of these items is TWO
            # lines below it in the plaintext email. This is pretty brittle,
            # and should probably be done with XML-parsing in the HTML message
            # in the future.
            # TODO: Un-brittle this.
            line = text_msg_lines[i]
            if "Confirmation Code:" in line:
                out_msg['aclu_confirmation_code'] = text_msg_lines[i + 2]
            elif "Gift Amount: " in line:
                out_msg['amount'] = text_msg_lines[i + 2]

        # Ensures that the values are stripped of excess whitespace.
        return {k: v.strip() for k, v in out_msg.iteritems()}
    except:
        # We could do better error-handling here, but for now, we just want
        # the lambda to fail quickly.
        # TODO: Reply to emails using SES and tell the user that their email
        # was not recognized.
        raise ValueError("Message was not a valid ACLU MIME message file.")


"""
The organization parser lookup. The guesser references functions inside here
to parse the incoming email. If it fails to match, it uses the default parser,
which is pretty dumb right now.
"""
OrganizationParsers = {
    'ACLU': parse_email_aclu,
    # TODO: Need default option here.
}


def guess_organization_parser(msg):
    """
    Given an email.Message, picks the right parser to use to gobble up the
    relevant information from the copytext.

    Arguments:
        msg (email.Message): The message to parse

    Returns:
        function: The function to use to parse the email
    """
    if "Thank you for your gift to the ACLU" in msg['subject']:
        return OrganizationParsers['ACLU']
    else:
        return OrganizationParsers['default']


def parse_email(raw_msg):
    """
    Performs the parsing, using `guess_organization_parser` to determine which
    parser to use.

    Arguments:
        raw_msg (str): The raw string of the MIME file stored in S3

    Returns:
        dict: In the form defined above.
    """
    msg = email.message_from_string(raw_msg)
    parser = guess_organization_parser(msg)
    return parser(msg)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8')
    )
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        message_parsed = parse_email(response['Body'].read())
        print("MESSAGE: " + json.dumps(message_parsed))
        return message_parsed
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. ' +
            'Make sure they exist and your bucket is in the ' +
            'same region as this function.'.format(key, bucket)
        )
        raise e

# print(parse_email(open('./aclu.mime', 'rt').read()))
