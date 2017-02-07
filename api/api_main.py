from flask import Flask, redirect
from flask_restful import Api
from flask_restful_swagger import swagger
import os

from api.campaign import Campaign, CampaignProperties

# Setup App
app = Flask(__name__)
#pi = Api(app)
api = swagger.docs(Api(app), apiVersion='0.1',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec', description='Donatemates API')


# Service to manage stories
api.add_resource(Campaign, '/campaign',
                           '/campaign/')

api.add_resource(CampaignProperties, '/campaign/<campaign_id>',
                                     '/campaign/<campaign_id>/')


@app.route('/')
def root():
    return redirect('api/spec.html')


# We only need this for local development.
if __name__ == '__main__':
    if "DEBUG_MODE" in os.environ:
        if os.environ("DEBUG_MODE").lower() == "true":
            debug_mode = True
        else:
            debug_mode = False
    else:
        debug_mode = False
    app.run(debug=debug_mode)
