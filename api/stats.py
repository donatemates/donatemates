from flask_restful import reqparse, Resource, abort
from api.aws import DynamoTable
from flask_restful_swagger import swagger
import arrow
import shortuuid
import uuid
from .util import clean_dynamo_response, send_email
from .charity import SUPPORTED_CHARITIES


class Stats(Resource):

    def __init__(self):
        super(Resource, self).__init__()
        self.campaign_table = DynamoTable('campaigns')
        self.donation_table = DynamoTable('donations')

    @swagger.operation(
        notes='Get global stats for the site',
        nickname='Get Site Stats',
        parameters=[])
    def get(self):
        """Get Site Stats"""


        return item, 200
