from abc import ABCMeta, abstractmethod
import email
import re


class CharityParser(object):
    """Parent Class for Charity Parsers"""
    __metaclass__ = ABCMeta

    def __init__(self, raw_email):
        self.raw_email = raw_email
        self.subject = None
        self.to_email = None
        self.from_email = None
        self.date = None
        self.plaintext = None
        self.html = None
        self.preprocess()

    @abstractmethod
    def parse_email(self):
        """
        Method to parse an email message

        Arguments:
            None

        Returns:
            (dict): Values to save in the DB. At a minimum should be:
                donor_name
                donor_email
                donation_cents
        """
        raise NotImplementedError

    @abstractmethod
    def is_receipt(self):
        """
        Method to check if an email is a receipt for this charity by parsing
        the email.

        Arguments:
            None

        Returns:
            (bool): True if it is the receipt for this charity
        """
        raise NotImplementedError

    def centify_donation_string(self, donation_string):
        """
        Converts a donation into cents.

        Arguments:
            donation_string (str): A string, like "$200.00"

        Returns:
            int: Cent amount (USD)
        """
        if "$" in donation_string:
            donation_string = donation_string.replace(",", "")
            donation_string = donation_string.strip("$")
            return int(100 * float(donation_string))
        else:
            raise ValueError("Cannot parse non-USD donations yet.")

    def parse_addressbook_email(self, email_string):
        """
        Parses addressbook-emails of the form "Name <email>"

        Arguments:
            email_string (str): The string to parse

        Returns:
            name (str), email (str)
        """
        results = re.findall(r"[\"']{0,1}(.*)['\"]{0,1}\s*<(.*\@.*)>", email_string)
        if len(results) > 0:
            return results[0]
        else:
            raise ValueError(
                "{} was not a valid address-book string.".format(email_string)
            )

    def preprocess(self):
        """
        Method to preprocess a raw email message into components
        """
        msg = email.message_from_string(self.raw_email)
        self.subject = msg["subject"]
        self.to_email = msg["to"]
        self.from_email = msg["from"]
        self.date = msg["date"]

        for idx, part in enumerate(msg.get_payload()):
            if idx == 0:
                self.plaintext = part
            else:
                self.html = part

    def get_campaign_id(self):
        """
        Function to get the campaign ID

        Returns:
            (str): the campaign ID
        """
        # check if the to email has been parsed and use that
        if not self.to_email:
            self.preprocess()

        return self.to_email.split("-")[1].split("@")[0]
