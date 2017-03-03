import boto3
from money import Money


class DonatematesEmail(object):
    """Class to handle sending all emails"""

    def __init__(self, donor_address=None, campaigner_address=None):
        self.campaigner_address = campaigner_address
        self.donor_address = donor_address

    def send_campaign_does_not_exist(self):
        """Method to send an email when the campaign doesn't exist (based on the email address used by donor)

        Returns:
            None
        """
        email_msg = u"Sorry, the campaign email address you used does not appear to be valid. "
        email_msg += u"\r\nDouble check the campaign email address and forward your receipt again!"
        subject = u"Donatemates: Campaign not found"
        self.send_email(self.donor_address, subject, email_msg, self.lame_html(email_msg))

    def send_campaign_cancelled(self):
        """Method to send a confirmation email to a donor when the campaign has been cancelled

        Returns:
            None
        """
        email_msg = u"The matching campaign you just tried to contribute to is no longer active. Sorry about that!"
        subject = u"Donatemates: Campaign not active"
        self.send_email(self.donor_address, subject, email_msg, email_msg)

    def send_duplicate_receipt(self, campaign_id, receipt_id, email_key):
        """Method to send an email when a duplicate receipt is detected

        Returns:
            None
        """
        email_msg = u"Sorry, we weren't able to process your donation as it looks like you've already submitted it to Donatemates for a match campaign. "
        email_msg += u"\r\nIf you think this was an error, please forward this email to help@donatemates.com and we'll look into it. Thanks!"
        email_msg += u"\r\n\r\nThanks!\r\n - Donatemates"
        email_msg += u"\r\n \r\n \r\n \r\nrequest_id: {}/{}/{}".format(campaign_id, receipt_id, email_key)

        subject = u"Donatemates: Unable to process donation"

        self.send_email(self.donor_address, subject, email_msg, self.lame_html(email_msg))

    def send_donation_confirmation(self, donation):
        """Method to send a confirmation to a donor

        Args:
            donation(int): Donation amount in cents

        Returns:
            None
        """
        donation = Money(amount=(donation / 100), currency="USD")
        donation = donation.format('en_US').split(".")[0]

        email_msg = u"Thank you for your donation of {}!\r\n We've added it to the match campaign and have let the matcher know as well.".format(donation)
        email_msg += u"\r\n\r\nThanks!\r\n - Donatemates"

        subject = u"Donatemates: Donation confirmation"

        self.send_email(self.donor_address, subject, email_msg, self.lame_html(email_msg))

    def send_campaign_update(self, donor_name, donation, campaign_total, campaign_target):
        """Method to send a confirmation to a donor

        Args:
            donor_name(str): Name of the donor
            donation(int): Donation amount in cents
            campaign_total(int): Campaign total to date in cents
            campaign_target(int): Campaign match target in cents

        Returns:
            None
        """
        donation = Money(amount=(donation / 100), currency="USD")
        donation = donation.format('en_US').split(".")[0]

        campaign_total = Money(amount=(campaign_total / 100), currency="USD")
        campaign_total = campaign_total.format('en_US').split(".")[0]

        campaign_target = Money(amount=(campaign_target / 100), currency="USD")
        campaign_target = campaign_target.format('en_US').split(".")[0]

        email_msg = u"Good news! {} just donated {} to your campaign! ".format(donor_name, donation)
        email_msg += u"\r\nYou're at {} out of the total {} you've offered to match.".format(campaign_total,
                                                                                             campaign_target)

        subject = u"Donatemates: Campaign Update"

        self.send_email(self.campaigner_address, subject, email_msg, self.lame_html(email_msg))

    def send_campaign_matched(self, donor_name, donation, campaign_total, campaign_target):
        """Method to send a confirmation to a campaigner when their campaign has been matched

        Args:
            donor_name(str): Name of the donor
            donation(int): Donation amount in cents
            campaign_total(int): Campaign total to date in cents
            campaign_target(int): Campaign match target in cents

        Returns:
            None
        """
        donation = Money(amount=(donation / 100), currency="USD")
        donation = donation.format('en_US').split(".")[0]

        campaign_total = Money(amount=(campaign_total / 100), currency="USD")
        campaign_total = campaign_total.format('en_US').split(".")[0]

        campaign_target = Money(amount=(campaign_target / 100), currency="USD")
        campaign_target = campaign_target.format('en_US').split(".")[0]

        email_msg = u"Congrats! {} just donated {} to your campaign! ".format(donor_name, donation)
        email_msg += u"\r\nYou have now raised {}, achieving your {} match target!".format(campaign_total,
                                                                                           campaign_target)

        subject = u"Donatemates: Campaign Matched!"

        self.send_email(self.campaigner_address, subject, email_msg, self.lame_html(email_msg))

    def send_campaign_created(self, campaign_id, secret_id):
        """Method to send a confirmation to a campaigner when their campaign has been matched

        Args:
            campaign_id(str): UUID for the campaign
            secret_id(str): Secret UUID used to validate original campaigner

        Returns:
            None
        """
        email_msg = u"You just created a matching campaign with Donatemates! "
        email_msg += u"\r\nKeep track of your campaign and share with your friends and followers here: https://donatemates.com/campaign/{}. ".format(campaign_id)
        email_msg += u"\r\n \r\nIf you want to cancel your campaign in the future, visit this link: https://donatemates.com/cancel/{}/{}".format(campaign_id, secret_id)

        subject = u"Donatemates: Campaign Created"

        self.send_email(self.campaigner_address, subject, email_msg, self.lame_html(email_msg))

    def lame_html(self, plaintext):
        """Temporary conversion from plain-text to html until better emails are created"""
        return plaintext.replace("\r\n", "<br>")

    def send_email(self, to_address, subject, plain_text, html):
        """
        Function to send an email from the default address

        Args:
            to_address(str): The email address to send to
            subject(unicode): The email message subject
            plain_text(unicode): The email message body in plain-text format
            html(unicode): The email message body in html format

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
                        'Data': plain_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html,
                        'Charset': 'UTF-8'
                    }
                }
            })

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("**** ERROR: Failed to send email to: {} - Error: {}".format(to_address, response))
