import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os
import arrow


class DynamoTable(object):
    """Class to wrap a dynamoDB table"""
    STACK_NAME = os.environ["STACK_NAME"]

    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        self.table_name = '{}.{}.donatemates'.format(DynamoTable.STACK_NAME, table_name)
        self.table = self.dynamodb.Table(self.table_name)

    def dict_to_item(self, attributes):
        """Method to convert a dictionary to a properly formatted item

        Args:
            attributes(dict): The input data dictionary with all attributes

        Returns:
            (dict): A reformatted dictionary
        """
        item = {}
        for attr in attributes:
            if type(attributes[attr]) is str:
                item[attr] = {'S': attributes[attr]}
            if type(attributes[attr]) is unicode:
                item[attr] = {'S': attributes[attr]}
            elif type(attributes[attr]) is int:
                item[attr] = {'N': "{}".format(attributes[attr])}
            elif type(attributes[attr]) is float:
                item[attr] = {'N': "{}".format(attributes[attr])}
            elif type(attributes[attr]) is long:
                item[attr] = {'N': "{}".format(attributes[attr])}
            elif type(attributes[attr]) is list:
                item[attr] = {'L': attributes[attr]}
        return item

    def put_item(self, data):
        """Method to create an item

        Args:
            data (dict): A dictionary of attributes to put

        Returns:
            None
        """
        response = self.table.put_item(Item=data,
                                       ReturnValues='NONE',
                                       ReturnConsumedCapacity='NONE',
                                       ReturnItemCollectionMetrics='NONE')

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error writing item to table: {}".format(response['ResponseMetadata']))

    def get_item(self, data):
        """Method to get an item

        Args:
            data (dict): A dictionary of attributes to put

        Returns:
            (dict)
        """
        try:
            response = self.table.get_item(Key=data,
                                           ConsistentRead=True)
        except ClientError as err:
            raise IOError("Error getting item: {}".format(err.message))

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise IOError("Error getting item: {}".format(response['ResponseMetadata']))

        if "Item" in response:
            return response["Item"]
        else:
            return None

    def delete_item(self, data):
        """Method to get an item

        Args:
            data (dict): A dictionary of attributes to access an item (hash and sort keys)

        Returns:
            None
        """
        try:
            response = self.table.delete_item(Key=data)

        except ClientError as err:
            raise IOError("Error deleting item: {}".format(err.message))

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise IOError("Error deleting item: {}".format(response['ResponseMetadata']))

    def query_hash(self, hash_name, hash_value, index=None, forward=True, limit=None, projection=None):
        """Method to query an index

        Args:
            data (dict): A dictionary of attributes to put

        Returns:
            (dict)
        """
        params = {"ScanIndexForward": forward,
                  "KeyConditionExpression": Key(hash_name).eq(hash_value)}
        if index:
            params["IndexName"] = index
        else:
            # If primary index, consistent read
            params["ConsistentRead"] = True

        if limit:
            params["Limit"] = limit

        if projection:
            params["ProjectionExpression"] = projection

        response = self.table.query(**params)

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

        return response["Items"]

    def update_attribute(self, key_dict, attribute_name, attribute_value):
        """Method to update a single attribute in a record

        Args:
            key_dict (dict): A dictionary containing the keys/values to query on. Supports simple and compound keys
            attribute_name (str):
            attribute_value (str):

        Returns:
            None
        """
        response = self.table.update_item(Key=key_dict,
                                          UpdateExpression="SET {} = :updated".format(attribute_name),
                                          ExpressionAttributeValues={':updated': '{}'.format(attribute_value)})

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

        # TODO: Check if any sort of validation on a update should done. DynamoDB seems lax here.
        #if "Attributes" in response:
        #    if len(response["Attributes"]) == 0:
        #        raise ValueError("Specified key does not exist. Update failed.")
        #else:
        #    raise ValueError("Specified key does not exist. Update failed.")

    def increment_attribute(self, key_dict, attribute_name, increment_value):
        """Method to increment a single attribute in a record

        Args:
            key_dict (dict): A dictionary containing the keys/values to query on. Supports simple and compound keys
            attribute_name (str): The attribute to increment
            increment_value (int): The amount to increment the attribute by

        Returns:
            None
        """
        response = self.table.update_item(Key=key_dict,
                                          UpdateExpression="SET {} = {} + :increment".format(attribute_name,
                                                                                             attribute_name),
                                          ExpressionAttributeValues={':increment': increment_value},
                                          ReturnValues="UPDATED_NEW")


        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

    def increment_map_attribute(self, key_dict, attribute_name, map_key_name, increment_value):
        """Method to increment a single attribute in a record

        Args:
            key_dict (dict): A dictionary containing the keys/values to query on. Supports simple and compound keys
            attribute_name (str): The attribute to increment
            increment_value (int): The amount to increment the attribute by

        Returns:
            None
        """
        response = self.table.update_item(Key=key_dict,
                                          UpdateExpression="SET {}.#s = if_not_exists({}.#s, :zero) + :increment".format(attribute_name,
                                                                                                   attribute_name),
                                          ExpressionAttributeNames={"#s": map_key_name},
                                          ExpressionAttributeValues={':increment': increment_value,
                                                                     ':zero': 0},
                                          ReturnValues="UPDATED_NEW")

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

    def query_24hr(self, hash_key, hash_value, sort_key, date_str):
        """Method to query for a date range for the day provided in the date_str

        Date_str must be in ISO-8601

        This assumes you are "centering" the 24hr block from midnight-midnight EST

        Args:
            hash_key (str): Hash key name
            sort_key (str): Sort key name
            date_str (str): The date string containing the day to query in UTC time

        Returns:
            list
        """
        # Convert ISO time to be EST
        date_in = arrow.get(date_str)
        date_in_est = date_in.to('EST')

        # Compute start date str
        start_date = date_in_est.replace(hour=0, minute=0)

        # Compute end date str
        date_range = start_date.span('day')

        response = self.table.update_item(Key={hash_key: hash_value},
                                          KeyConditionExpression="{} >= :morning AND {} <= :midnight".format(sort_key,
                                                                                                             sort_key),
                                          ExpressionAttributeValues={':morning': date_range[0].isoformat(),
                                                                     ':midnight': date_range[1].isoformat()},
                                          ReturnValues="UPDATED_NEW")

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

        if "Items" in response:
            return response["Items"]
        else:
            return []

    def query_most_recent(self, hash_key, hash_value, sort_key, date_str, limit=1):
        """Method to query for the record most recently in the past based on the date_str

        Date_str must be in ISO-8601

        Args:
            hash_key (str): Hash key name
            sort_key (str): Sort key name
            date_str (str): The date string containing the day to query in UTC time

        Returns:
            dict
        """
        response = self.table.query(KeyConditionExpression=Key(hash_key).eq(hash_value) & Key(sort_key).lte(date_str),
                                    Limit=limit,
                                    ScanIndexForward=False,
                                    Select="ALL_ATTRIBUTES")

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

        if "Items" in response:
            if response["Items"]:
                return response["Items"]
            else:
                return []
        else:
            return []

    def query_biggest(self, hash_key, hash_value, num_items, index=None, forward=False):
        """Method to query for the largest N records

        Args:
            hash_key (str): Hash key name
            hash_value (str): Hash key value
            num_items (int): The number of items to return
            index (str): Name of index if not primary
            forward (bool): flag indicating sort direction

        Returns:
            dict
        """
        params = {"ScanIndexForward": forward,
                  "KeyConditionExpression": Key(hash_key).eq(hash_value),
                  "Select": "ALL_ATTRIBUTES",
                  "Limit": num_items}

        if index:
            params["IndexName"] = index
            params["Select"] = "ALL_PROJECTED_ATTRIBUTES"
        else:
            # If primary index, consistent read
            params["ConsistentRead"] = True

        response = self.table.query(**params)

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception("Error getting item: {}".format(response['ResponseMetadata']))

        if "Items" in response:
            if response["Items"]:
                return response["Items"]
            else:
                return []
        else:
            return []

    def integer_sum_attribute(self, hash_key, hash_value, attribute_name, index=None):
        """Method to query for the largest N records

        Args:
            hash_key (str): Hash key name
            hash_value (str): Hash key value
            attribute_name (str): Name of the attribute to sum
            index (str): Name of index if not primary

        Returns:
            (int) Sum of the attribute
        """
        client = boto3.client('dynamodb', region_name="us-east-1")
        paginator = client.get_paginator('query')
        params = {"KeyConditionExpression": "{} = :queryVal".format(hash_key),
                  "ExpressionAttributeValues": {":queryVal": {"S": "{}".format(hash_value)}},
                  "Select": "ALL_ATTRIBUTES",
                  "TableName": self.table_name,
                  "PaginationConfig": {'PageSize': 500}
                  }
        if index:
            params["IndexName"] = index
            params["Select"] = "ALL_PROJECTED_ATTRIBUTES"

        response_iterator = paginator.paginate(**params)
        total_value = 0
        for page in response_iterator:
            for item in page["Items"]:
                total_value += int(item[attribute_name]["N"])

        return total_value

    def scan_table(self, eval_function, result_dict, attribute_str):
        """Method to scan a table, passing each item into an evaluation function

        Args:
            eval_function (function): Function to process the items
            attribute_str (str): Comma separated string of attributes to get

        Returns:
            (dict) Result of the scan
        """
        client = boto3.client('dynamodb', region_name="us-east-1")
        paginator = client.get_paginator('scan')
        params = {"ProjectionExpression": attribute_str,
                  "TableName": self.table_name,
                  "PaginationConfig": {'PageSize': 500}
                  }

        response_iterator = paginator.paginate(**params)
        for page in response_iterator:
            result_dict = eval_function(page["Items"], result_dict)

        return result_dict
