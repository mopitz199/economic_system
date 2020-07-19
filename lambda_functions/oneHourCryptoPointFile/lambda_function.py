import json
import boto3
import os
import requests
from datetime import datetime


def lambda_handler(event, context):
    coinmarketcap_host = os.environ['COINMARKETCAP_HOST']
    coinmarketcap_headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.environ['COINMARKETCAP_PRO_API_KEY'],
    }

    url = f'https://{coinmarketcap_host}/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
    }
    response = requests.get(
        url,
        params=parameters,
        headers=coinmarketcap_headers
    )
    data = json.loads(response.text)

    s3 = boto3.client('s3')

    with open("/tmp/temp_data.json", "w") as f:
        json.dump(data, f)

    name = datetime.utcnow().strftime("%Y%m%d%H0000")
    s3.upload_file("/tmp/temp_data.json", "cryptocurrency-listings-latest", f"{name}.json")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
