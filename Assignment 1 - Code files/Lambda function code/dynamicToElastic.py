import json
import boto3
from boto3.dynamodb.conditions import Key
import requests

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp_restaurants')
    fn = getattr(requests, 'post')
    resp = table.scan()
    i = 1
    url = 'https://search-restaurants-ovnnbuc6agelefjdocq2sxrkqm.us-east-1.es.amazonaws.com/restaurants/restaurants'
    headers = {"Content-Type": "application/json"}
    session = requests.Session()
    session.auth = ('Revati24','Revati24@')
    while True:
        for item in resp['Items']:
            body = {"RestaurantID": item['businessId'], "Cuisine": item['cuisine']}
            r = session.post(url, data=json.dumps(body), headers=headers)
            i += 1
        if 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
        else:
            break;
    return {
        'statusCode': 200,
        'body': json.dumps('Data uploaded to ES!')
    }