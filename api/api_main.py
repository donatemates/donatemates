from flask import Flask, redirect
from flask_restful import Api
from flask_restful_swagger import swagger
import os

from api.campaign import Campaign, CampaignProperties
from api.charity import Charities


def is_debug_mode():
    """Method to check if the stack is in debug mode

    Returns:
        (bool)
    """
    if os.environ.get('DEBUG_MODE'):
        if os.environ.get('DEBUG_MODE').lower() == "true":
            debug_mode = True
        else:
            debug_mode = False
    else:
        debug_mode = False

    return debug_mode


app = Flask(__name__)
if is_debug_mode():
    api = swagger.docs(Api(app), apiVersion='0.1',
                       resourcePath='/',
                       produces=["application/json", "text/html"],
                       api_spec_url='/api/spec', description='Donatemates API')
else:
    # Don't build swagger docs
    api = Api(app)


# Service to manage stories
api.add_resource(Campaign, '/campaign',
                           '/campaign/')

api.add_resource(CampaignProperties, '/campaign/<campaign_id>',
                                     '/campaign/<campaign_id>/')

api.add_resource(Charities, '/charities',
                            '/charities/')


@app.route('/')
def root():
    return redirect('api/spec.html')


@app.after_request
def after_request(response):
    if is_debug_mode():
        # If in debug mode, allow CORS
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Launch in dev mode if desired
if __name__ == '__main__':
    app.run(debug=is_debug_mode())
