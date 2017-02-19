# donatemates
donatemates.com - easy, automated donation matching.


## Overview
This repo contains all the source code for the donatemates serverless platform, including deployment automation.

`/api` - A python package containing a Flask base REST API application and tests

`/frontend` - The donatemates website

`/manage` - A python package containing classes for depolyment and management of the donatemates platform

`/dmlambda` - A python package containing email parsing software

`/donatemates.py` - A command line tool to manage deployments


## Getting Started
This assumes you are working in a pre-configured AWS account. If you are cloning donatemates and running from scratch, read the *Manual Configuration* section.

- `mkdir` and `cd` to a directory of your choice

- Clone the repo

	```
	git clone https://github.com/donatemates/donatemates.git
	```

- We use the awesome [zappa](https://github.com/Miserlou/Zappa) package to manage much of the deployment, which requires you run in a virtual environment. Also, **be sure to use Python 2.7**, as Python3 is not yet supported by Lambda.

	- Using [virtualenv](https://virtualenv.pypa.io/en/stable/):

		```
		virtualenv dm-env
		. dm-env/bin/activate
		```

	- Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

		```
		mkvirtualenv dm-env
		```

- Install Python dependencies into the virtual environment

	```
	cd ./donatemates
	pip install -r requirements.txt
	```

- Setup your system level AWS credentials

	- Currently the automation software loads the system level AWS credentials (e.g. ~/.aws/credentials).


- Set the `STACK_NAME` environment variable
	- Currently we are using an environment variable to indicate which "stack" you are building. This is primarily used through some of the tests, and eventually will be removed.

	```
	export STACK_NAME=<name_of_your_stack>
	```

- Finally, we're using LetsEncrypt to provision SSL certs for the API and must generate a key.
	- You need to provide a secret key for this process. For official donatemates stacks (including dev) contact [@dkleissa](https://github.com/dkleissa).
	- To generate a new key, run the following command at the repo root. The first time it runs it can take up to 45 minutes, but after that it's ~60 seconds. Your API domain won't be available until this process completes and DNS propagates.

**DO NOT COMMIT THIS FILE**

```
cd <repo_root>
openssl genrsa 2048 > account.key;
```

**DO NOT COMMIT THIS FILE**

## Deploying

To get a donatemates stack up, you need to deploy the API, frontend, database, and email processing lambda fuction. The `donatemates.py` file is the main entry point for a tool that automates this process:

```
workon dm-env
python donatemates.py <action> <stack_name>
```

The tool is setup with the following `stack_names`:

- `dean` - dev stack for @dkleissa
- `sahil` - dev stack for @slavingia
- `jordan` - dev stack for @j6k4m8
- `production` - the production environment


The following `actions` are supported:

- `create` - deploys the stack (API Gateway, Lambda, CloudWatch, SES, CloudFront, and DynamoDB)
- `update` - updates the API code and frontend
- `update_frontend` - updates the frontend only
- `delete` - tears down the stack. Buckets are emptied but remain along with some DNS and SES configuration to speed up re-deployments
- `populate` - populates a stack with some dummy data for testing

Each stack is deployed into its own subdomain (except production). Once deployment is complete:

- API: https://api-{stack_name}.donatemates.com
- Frontend: https://{stack_name}.donatemates.com
- Email Endpoint: {anything|campaign_id}@{stack_name if not prod}.donatemates.com

## Running Tests

### API Tests
Using nose2 for unit and integration tests. Unit tests are mocked and integration run in temporary generated databases

run unit tests:

```
cd <repo_root>/api
nose2
```

run integration tests:

```
cd <repo_root>/api
nose2 -c inttest.cfg
```

In addition there are some "production" level integration tests that will stress the database a bit and should only be run on production. To enable, set the environment variable before testing as shown below:

```
cd <repo_root>/api
export RUN_SCALE_TESTS=True
nose2 -c inttest.cfg
```

## Debugging

Zappa has a built in tail function for watching logs. To use it, activate your virutalenv and run the tail command manually

```
workon dm-env
zappa tail <stack_name>
// hit ctrl+c to stop.
```

You can run the API locally like any Flask app by executing the `donatemates/api/api_main.py` file in python. If you set the environment variable `DEBUG_MODE=true` the Flask server will run in debug mode and Swagger based API documentation and interactive browser will be available.

All "dev" stack APIs have `DEBUG_MODE=true` by default. In addition they have CORS enabled to aid in local frontend development.

## Manual Configuration

Not everything is 100% automated. This is not a perfect list yet, but you must manually:

- Setup your intial hosted zone in Route53
- Setup your domain identity in SES
- Add rules to SES for writing inbound emails to S3 (do this after the automation tool creates the S3 buckets with the appropriate policies for you).
- Initial deployment of the frontend using the AWS static website builder (the automation tool updates this initial configuration) and update the zappa config file.
