import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests
from botocore.exceptions import ClientError
from botocore.vendored.requests.auth import HTTPBasicAuth
import logging

def lambda_handler(event, context):
    
    # DynamoDB config
    client = boto3.resource('dynamodb')
    table = client.Table('yelp_restaurants')
   
    # Queue specification
    sqs = boto3.resource('sqs')
    sqs_client = boto3.client('sqs')
    queue = sqs.get_queue_by_name(QueueName='RestaurantRequests')
    url = "https://sqs.us-east-1.amazonaws.com/746458809742/RestaurantRequests"
    
    # Poll the queue
    messages = queue.receive_messages()
    # Iterate over the messages received from the queue
    for msg in messages:
        # Spliting the message based on comma and formatting to generate an email
        parts_of_msg = msg.body.split(",")
        # Elasticsearch fetch based on cuisine
        es_query = "https://search-restaurants-ovnnbuc6agelefjdocq2sxrkqm.us-east-1.es.amazonaws.com/restaurants/_search?q=" + parts_of_msg[1]
        response = requests.get(es_query, auth=HTTPBasicAuth('Revati24', 'Revati24@'))
        suggestions = json.loads(response.text)['hits']['hits']
        # iterate for 4 time. _source: RestaurantID. Fetch this particular businessId from dynamoDb
        restaurants_suggested = str()
        restaurants_suggested = "\n"
        number = 1
        try:
            for suggestion in suggestions:
                if number > 5:
                    break
                restaurant_id = suggestion['_source']['RestaurantID']
                # Get the restaurant name and address from dynamoDB
                response = table.scan(FilterExpression=Attr('businessId').eq(restaurant_id))
                item = response['Items'][0]
                restaurants_suggested += str(number) + "] " + item['name'] + " at " + item['address'] + " \n"
                number += 1
            # Constructing email body
           
            msg_to_send = "Hello! Here are my " + parts_of_msg[1] + " restaurant suggestions for "+ str(parts_of_msg[2]) +" people, for "+parts_of_msg[3]+" at " + parts_of_msg[4] + restaurants_suggested + " . Enjoy your meal!"
            # Sending email using SES service
            client = boto3.client("ses", region_name="us-east-1")
            CHARSET = "UTF-8"
            response = client.send_email(
                Destination={
                    "ToAddresses": [
                        parts_of_msg[5],
                    ],
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": CHARSET,
                            "Data": msg_to_send,
                        }
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": "Restaurant suggestions",
                    },
                },
                Source="rst8739@nyu.edu",
            )
            # deleting the message from the queue
            sqs_client.delete_message(
                QueueUrl=url,
                ReceiptHandle=msg.receipt_handle
            )
        except Exception as ex:
            print(ex)
    return {
        'statusCode': 200,
        'body': json.dumps('Restaurant suggestions sent successfully!')
    }
