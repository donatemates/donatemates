from .charity import Charity


class MSFParser(Charity):
    """Parsing class for the ACLU"""

    def parse_email(self):
        """
        Method to parse an email message

        Arguments:
            None

        Returns:
            (dict): Values to save in the DB. At a minimum should be:
                "donor_name"
                "donor_email"
                "donation_cents"
        """
        raise NotImplementedError

    def is_receipt(self):
        """
        Method to check if an email is a receipt for this charity by parsing
        the subject line.

        Args:
            None

        Returns:
            (bool): True if it is the receipt for this charity
        """
        return "Thank you from Doctors Without Borders" in self.subject

