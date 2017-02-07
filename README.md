# donatemates
donatemates.com - easy, automated donation matching.


## Overview
asdf

`/api` - A python package containing a Flask base REST API application
 
`/manage` - A python package for depolyment and management of the donatemates backend

`/donatemates.py` - A command line tool to manage deployments


## Configure
First, setup your virtualenv and install the requirements. Must be python 2.7 as we're using Lambda and it's still limited.

Currently loading credentials manually out of a json file. Copy the example file and populate.

```
cp aws_credentials.json.example aws_credentials.json
```

Also using 2 environment variables at the moment to control what gets loaded, so you have to set them

```
export STACK_NAME=<name_of_your_stack>
export AWS_CREDENTIALS=<path_to_cred_file_above>
```

Finally, we're using LetsEncrypt to provision SSL certs. You need to create a secret key for this process.
The first time it runs it can take up to 45 minutes, but after that it's ~60 seconds.

**DO NOT COMMIT THIS FILE**

```
cd <repo_root>
openssl genrsa 2048 > account.key;
```

## Deploying A Stack

The `donatemates.py` file is the main entry point for managing stacks:

```
workon donatemates
python donatemates.py <action> <stack_name>
```

The manage app is setup with the following `stack_names`:

- `dean` - dev stack for dean
- `jordan` - dev stack for jordan
- `stage` - stack for testing before production
- `production` - the production environment


The following `actions` are supported:

- `create` - deploys the stack (API Gateway, Lambda, CloudWatch, and DynamoDB)
- `update` - updates the API code and redeploys
- `delete` - deletes everything from AWS
- `populate` - populates a stack with some dummy data for testing


You can pre-populate a stack with intial data using the `populate` command. It loads 1 story, publishes it nationally, adds some stats, and sets _DebugUser_ as an admin. The story ID is `2a5a480eaa7341b69ef4a9ba337618c2` and the DummyUser (default authenticated user until auth is fully integrated) is `20018`.

When adding a role, additional args are needed:

```
python donatemates.py <action> <stack_name> -u <username> -r <role>
```

Valid roles are `author`, `editor`, and `admin`.

## Debugging

Zappa has a built in tail function for watching logs. To use it, activate your virutalenv and run the tail command manually

```
workon donatemates
zappa tail <stack_name>
```

hit ctrl+c to stop.

## Running Tests

Using nose2 for unit and integration tests. unit tests are mocked and integration run in temporary databases

run unit tests:

```
cd api
nose2
```

run integration tests:

```
export STACK_NAME=<stack_name>
export AWS_CREDENTIALS=<path_to_cred_file>
cd api
nose2 -c inttest.cfg
```



