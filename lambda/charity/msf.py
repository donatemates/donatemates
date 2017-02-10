from .charity import Charity


class Msf(Charity):
    """Parsing class for the ACLU"""

    def parse_email(self, msg):
        """
        Method to parse an email message

        Arguments:
            msg ({ body: str, subject: str }): The email's subject and body

        Returns:
            (dict): Values to save in the DB. At a minimum should be:
                "donor_name"
                "donor_email"
                "donation_cents"
        """
        raise NotImplementedError

    def is_receipt(self, msg):
        """
        Method to check if an email is a receipt for this charity by parsing
        the subject line.

        Args:
            msg ({ body: str, subject: str }): The email's subject and body

        Returns:
            (bool): True if it is the receipt for this charity
        """
        return "Thank you from Doctors Without Borders" in msg['subject']

