from flask_restful import Resource
from flask_restful_swagger import swagger
from copy import deepcopy


# Setup supported charities here. Parsing email lambda imports this variable!
SUPPORTED_CHARITIES = {
    "aclu": {
        "conversational_name": "the ACLU",
        "website": "https://action.aclu.org/donate-aclu?redirect=donate/join-renew-give",
        "class": "Aclu"
    },
    "msf": {
        "conversational_name": "Doctors Without Borders",
        "website": "https://donate.doctorswithoutborders.org/onetime.cfm",
        "class": "Msf"
    }
}


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
        # Format the JSON response
        charities = deepcopy(SUPPORTED_CHARITIES)
        for charity in charities:
            del charities[charity]["class"]

        return SUPPORTED_CHARITIES, 200
