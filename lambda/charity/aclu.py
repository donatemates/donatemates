from .charity import Charity


class Aclu(Charity):
    """Parsing class for the ACLU"""

    def parse_email(self):
        """Method to parse an email message

        Returns:
            (dict): Values to save in the DB. At a minimum should be "donor_name", "donor_email", and "donation_cents"
        """
        raise NotImplemented

    def is_receipt(self):
        """Method to check if an email is a receipt for this charity by parsing the subject line.

        Args:
            email_subject(str): The email's subject line

        Returns:
            (bool): True if it is the receipt for this charity
        """
        raise NotImplemented

