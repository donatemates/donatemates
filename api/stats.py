from flask_restful import Resource
from api.aws import DynamoTable
from flask_restful_swagger import swagger


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

        def campaign_count_func(items, result):
            """Method to count campaigns"""
            result["campaign_count"] += len(items)

        def donation_func(items, result):
            """Method to count campaigns"""
            for item in items:
                result["donation_count"] += 1
                result["total_donation_cents"] += int(item["donation_cents"]["N"])

        result = {"campaign_count": 0,
                  "donation_count": 0,
                  "total_donation_cents": 0}
        self.campaign_table.scan_table(campaign_count_func, result, "campaign_id")
        self.donation_table.scan_table(donation_func, result, "donation_cents")

        return result, 200
