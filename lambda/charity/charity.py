from abc import ABCMeta, abstractmethod
import email


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
            donation_string = donation_string.strip("$")
            return int(100 * float(donation_string))
        else:
            raise ValueError("Cannot parse non-USD donations yet.")

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

        # If not pre-processed and then pull out campaign_id
        return NotImplementedError
