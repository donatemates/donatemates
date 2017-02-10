from abc import ABCMeta, abstractmethod
import email


class Charity(object):
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
    def parse_email(self, msg):
        """
        Method to parse an email message

        Returns:
            (dict): Values to save in the DB. At a minimum should be:
            "donor_name"
            "donor_email"
            "donation_cents"
        """
        raise NotImplementedError

    @abstractmethod
    def is_receipt(self, msg):
        """
        Method to check if an email is a receipt for this charity by parsing
        the email.

        Arguments:
            email ({ body: str, subject: str})
        Returns:
            (bool): True if it is the receipt for this charity
        """
        raise NotImplementedError

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
