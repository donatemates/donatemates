from .charity import CharityParser


class PPParser(CharityParser):
    """Parsing class for Planned Parenthood"""

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
        donation_string = [word for word in self.plaintext.as_string().split() if "$" in word][0]
        transaction_id = [
            line.split(":")[1].strip()
            for line in self.plaintext.as_string().split('\n')
            if 'Transaction ID' in line
        ][0]
        if "<" in self.from_email:
            donor_name, donor_email = self.parse_addressbook_email(self.from_email)
        else:
            donor_name = donor_email = self.from_email
        return {
            "donation_cents": self.centify_donation_string(donation_string),
            "donation_raw": donation_string,
            "donor_name": donor_name,
            "donor_email": donor_email,
            "pp_transaction_id": transaction_id
        }

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

