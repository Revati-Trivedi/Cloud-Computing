import json

def lambda_handler(event, context):
    # TODO: Implement business logic of interaction with the database in the next assignment
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': 'Application under development. Search \
functionality will be implemented in Assignment 2!'
    }
