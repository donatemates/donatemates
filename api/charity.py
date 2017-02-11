from flask_restful import Resource
from flask_restful_swagger import swagger


# Setup supported charities here. Parsing email lambda imports this variable!
SUPPORTED_CHARITIES = [{
    "id": "aclu",
    "name": "ACLU",
    "conversational_name": "the ACLU",
    "donation_url": "https://action.aclu.org/donate-aclu?redirect=donate/join-renew-give",
    "class": "ACLUParser"
}, {
    "id": "msf",
    "name": "Doctors without Borders",
    "conversational_name": "Doctors Without Borders",
    "donation_url": "https://donate.doctorswithoutborders.org/onetime.cfm",
    "class": "MSFParser"
}]


class Charities(Resource):
    """
    A Charity is a flask resource that represents a single Charity such as
    MSF or ACLU.
    """

    def __init__(self):
        super(Resource, self).__init__()

    @swagger.operation(
        notes='Get the supported charities',
        nickname='Get Supported Charities')
    def get(self):
        """Get Supported Charities"""
        return SUPPORTED_CHARITIES, 200
