# from bs4 import BeautifulSoup
from .charity import CharityParser


class ACLUParser(CharityParser):
    """Parsing class for the ACLU"""

    def parse_email(self):
        """Method to parse an email message

        Arguments:
            None

        Returns:
            (dict): Values to save in the DB. At a minimum should be
                "donor_name"
                "donor_email"
                "donation_cents"
        """
        parsed_message = {}
        # soup = BeautifulSoup(self.html.as_string())

        plaintext_lines = self.plaintext.as_string().split('\n')
        try:
            for i in range(len(plaintext_lines)):
                # We happen to know that the value of each of these items is TWO
                # lines below it in the plaintext email. This is pretty brittle,
                # and should probably be done with XML-parsing in the HTML message
                # in the future.
                line = plaintext_lines[i]
                if "Confirmation Code:" in line:
                    parsed_message['aclu_confirmation_code'] = plaintext_lines[i + 2]
                elif "Gift Amount: " in line:
                    str_amount = plaintext_lines[i + 2]
                    parsed_message['donation_raw'] = str_amount
                    parsed_message['donation_cents'] = self.centify_donation_string(str_amount)

            # Ensures that the values are stripped of excess whitespace.
            if "<" in self.from_email:
                donor_name, donor_email = self.parse_addressbook_email(self.from_email)
            else:
                donor_name = donor_email = self.from_email

            parsed_message["donor_name"] = donor_name.strip()
            parsed_message["donor_email"] = donor_email.strip()
            return parsed_message
        except Exception as e:
            raise ValueError("Not a digestable ACLU email: {}".format(e))

    def is_receipt(self):
        """
        Method to check if an email is a receipt for this charity.

        Args:
            None

        Returns:
            (bool): True if it is the receipt for this charity
        """
        return "Thank you for your gift to the ACLU" in self.subject
