from boto3.dynamodb.types import Decimal


def clean_dynamo_response(data):
    """Method to convert dynamodb response types to something that is serializable by JSON

        Supports up to 1 nesting layer

    Args:
        data (dict): Input dictionary of data

    Returns:
        (dict)
    """
    for key in data:
        if type(data[key]) is dict:
            for secondary in data[key]:
                if type(data[key][secondary]) is Decimal:
                    data[key][secondary] = float(data[key][secondary])
        if type(data[key]) is Decimal:
                    data[key] = float(data[key])
    return data