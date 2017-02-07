from flask_restful import reqparse, Resource, abort
from api.aws import DynamoTable
from flask_restful_swagger import swagger
import arrow
import shortuuid
from .util import clean_dynamo_response


story_post_parser = reqparse.RequestParser()
story_post_parser.add_argument('charity_name', type=str, required=True, help='Name of charity')
story_post_parser.add_argument('campaigner_name', type=str, required=True, help='Campaingers name')
story_post_parser.add_argument('campaigner_email', type=str, required=True, help='Campaingers email')
story_post_parser.add_argument('match_cents', type=int, required=True, help='Target amount to match')

SUPPORTED_CHARITIES = {"aclu": "the ACLU"}


class Campaign(Resource):

    def __init__(self):
        super(Resource, self).__init__()
        self.table = DynamoTable('campaigns')

    @swagger.operation(
        notes='Service to create a new campaign',
        nickname='Create a Campaign',
        parameters=[
            {
                "name": "charity_name",
                "description": "Name of charity. Supported: {}".format(", ".join(SUPPORTED_CHARITIES.keys())),
                "required": True,
                "allowMultiple": False,
                "dataType": 'string',
                "paramType": "query"
            },
            {
                "name": "campaigner_name",
                "description": "Campainger's name",
                "required": True,
                "allowMultiple": False,
                "dataType": 'string',
                "paramType": "query"
            },
            {
                "name": "campaigner_email",
                "description": "Campainger's email",
                "required": True,
                "allowMultiple": False,
                "dataType": 'string',
                "paramType": "query"
            },
            {
                "name": "match_cents",
                "description": "Target amount to match in cents",
                "required": True,
                "allowMultiple": False,
                "dataType": 'integer',
                "paramType": "query"
            }
        ])
    def post(self):
        """Create a Campaign"""
        args = story_post_parser.parse_args()

        # Verify charity is supported
        if args["charity_name"] not in SUPPORTED_CHARITIES.keys():
            abort(400, description="Unsupported charity type: {}".format(args["charity_name"]))

        args["campaign_id"] = "{}-donation-matcher".format(shortuuid.uuid())
        args["campaign_status"] = "active"
        args['notified_on'] = arrow.utcnow().isoformat()
        args['created_on'] = arrow.utcnow().isoformat()
        args['secret_id'] = shortuuid.uuid()
        args['charity_context_name'] = SUPPORTED_CHARITIES[args["charity_name"]]

        # Put the object
        self.table.put_item(args)
        return {"campaign_id": args["campaign_id"]}, 201


class CampaignProperties(Resource):

    def __init__(self):
        super(Resource, self).__init__()
        self.campaign_table = DynamoTable('campaigns')
        self.dontation_table = DynamoTable('donations')

    @swagger.operation(
        notes='Get the properties of a campaign by ID',
        nickname='Get Campaign Details',
        parameters=[
            {
                "name": "campaign_id",
                "description": "UUID of the campaign",
                "required": True,
                "allowMultiple": False,
                "dataType": 'string',
                "paramType": "path"
            }])
    def get(self, campaign_id):
        """Get Campaign Details"""
        # Get the campaign
        data = {"campaign_id": campaign_id}
        item = None
        try:
            item = self.campaign_table.get_item(data)
        except IOError as e:
            abort(400, description=e.message)

        if not item:
            abort(404, description="Campaign '{}' not found".format(campaign_id))

        # Get donor amount stats
        amounts = self.dontation_table.query_biggest("campaign_id", campaign_id, 5, index="DonationIndex")

        # Get donor time stats
        donors = self.dontation_table.query_most_recent("campaign_id", campaign_id,
                                                        "donation_on", arrow.utcnow().isoformat(),
                                                        limit=5)

        item["large_donors"] = [{"donator_name": x["donator_name"],
                                 "donation_cents": float(x["donation_cents"])} for x in amounts]
        item["recent_donors"] = [{"donator_name": x["donator_name"],
                                  "donation_cents": float(x["donation_cents"])} for x in donors]

        # Sum donors
        # TODO: Add dynamic sum of all donations

        item = clean_dynamo_response(item)

        return item, 200
