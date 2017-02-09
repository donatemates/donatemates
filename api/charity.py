from flask_restful import Resource
from flask_restful_swagger import swagger

# Setup supported charities here. Parsing email lambda imports this variable!
SUPPORTED_CHARITIES = {"aclu": {"conversational_name": "the ACLU",
                                "website": "https://action.aclu.org/donate-aclu?redirect=donate/join-renew-give",
                                "class": "Aclu"}}


class Charities(Resource):

    def __init__(self):
        super(Resource, self).__init__()

    @swagger.operation(
        notes='Get the supported charities',
        nickname='Get Supported Charities')
    def get(self):
        """Get Supported Charities"""
        # Format the JSON response
        charities = SUPPORTED_CHARITIES
        for c in charities:
            del charities[c]["class"]

        return SUPPORTED_CHARITIES, 200
