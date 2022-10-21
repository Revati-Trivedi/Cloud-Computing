import json
import boto3

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    response = client.post_text(
        botName='DiningConcierge',
        botAlias='Test',
        userId='test_session',
        inputText=event["messages"][0]["unstructured"]["text"]
    ) 
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': response["message"]
    }
