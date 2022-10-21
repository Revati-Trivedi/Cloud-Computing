import json
import boto3
import urllib3
from datetime import datetime

def lambda_handler(event, context):
    # initiating connection to dynamodb table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp_restaurants')
    http = urllib3.PoolManager()
    # Scrap from the Yelp API and add the restaurants to the yelp-restaurants DynamoDB table
    restaurant_cuisine_type = ["mexican restaurants", "italian restaurants","ethiopian restaurants","chinese restaurants","japanese restaurants"]
    # Iterating over 5 different cuisine types
    for cuisine in restaurant_cuisine_type:
        offset = 0
        for i in range(0, 20):
            target_url = "https://api.yelp.com/v3/businesses/search?term='" + cuisine + "'&location=Manhattan&offset=" + str(offset) + "&limit=50"
            offset = offset + 50
            headers = { "Authorization": "Bearer mC45JfEKyZguFNsxemVRPIzsxdF4TIEU4RmfpfM8A3qGb62jUf709xa9H2c5kqBiAAOrqxdIXycpMyTLSpJw9KpPapZpWswj7IP28RzxcPLz0jwjOtqWo8qMzZZMY3Yx" } 
            restaurants = http.request('GET', target_url, headers = headers)
            restaurants_json = json.loads(restaurants.data)["businesses"]
            if len(restaurants_json) == 0:
                break
            index = 2
            bulk_data = str()
            # Iterate over the restaurants_json for 1000 times and store each record in the dynamodb along with insertedAtTimeStamp as current date and time
            for i in range(0, min(50, len(restaurants_json))):
                print(restaurants_json[i])
                restaurants_json[i]['insertedAtTimeStamp'] = str(datetime.now())
                table.put_item(Item = {
                'insertedAtTimeStamp': restaurants_json[i]['insertedAtTimeStamp'],
                'businessId': restaurants_json[i]['id'],
                'name': restaurants_json[i]['name'],
                'address': restaurants_json[i]['location']['display_address'][0] + "\n" + restaurants_json[i]['location']['display_address'][1], # (len(restaurants_json[i]['location']['display_address']) > 0?(restaurants_json[i]['location']['display_address'][0]): "" ) + "\n" + (len(restaurants_json[i]['location']['display_address']) > 1?(restaurants_json[i]['location']['display_address'][1]): ""),
                'zip code': restaurants_json[i]['location']['zip_code'],
                'reviews': restaurants_json[i]['review_count'],
                'ratings': str(restaurants_json[i]['rating']),
                'latitude': str(restaurants_json[i]['coordinates']['latitude']),
                'longitude': str(restaurants_json[i]['coordinates']['longitude']),
                'cuisine': cuisine
            })
            # Store restaurant id and cuisine in json format for insertion in elastic search
            break
        
   