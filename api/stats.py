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
        """Get Site Stats

        Response:
            campaign_count - total number of campaigns
            campaign_active_count - total number of active campaigns
            campaign_matched_count - total number of matched campaigns
            campaign_cancelled_count - total number of cancelled campaigns
            campaign_total_cents - total amount of pledged cents (sum of matched and active campaigns only)
            donation_count - total number of donations
            total_donation_cents - total amount of donations in cents

        """
        def campaign_count_func(items, result):
            """Method to count campaigns"""
            result["campaign_count"] += len(items)

            for item in items:
                if item["campaign_status"]["S"] == "active":
                    result["campaign_active_count"] += 1
                    result["campaign_total_cents"] += int(item["match_cents"]["N"])
                elif item["campaign_status"]["S"] == "matched":
                    result["campaign_matched_count"] += 1
                    result["campaign_total_cents"] += int(item["match_cents"]["N"])
                else:
                    result["campaign_cancelled_count"] += 1

        def donation_func(items, result):
            """Method to count campaigns"""
            for item in items:
                result["donation_count"] += 1
                result["total_donation_cents"] += int(item["donation_cents"]["N"])

        result = {"campaign_count": 0,
                  "campaign_active_count": 0,
                  "campaign_matched_count": 0,
                  "campaign_cancelled_count": 0,
                  "campaign_total_cents": 0,
                  "donation_count": 0,
                  "total_donation_cents": 0}
        self.campaign_table.scan_table(campaign_count_func, result, "campaign_id")
        self.donation_table.scan_table(donation_func, result, "donation_cents")

        return result, 200
