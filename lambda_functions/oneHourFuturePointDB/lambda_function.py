import json
import requests
import boto3
import os
from datetime import datetime

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[AwsLambdaIntegration()]
)

app_headers = {
    'Authorization': 'Token '+os.environ['TOKEN'],
    'Content-Type': 'application/json'
}
host = 'eb.economicapp.io'


def get_file(file_name, bucket_name):
    try:
        s3 = boto3.client('s3')
        file_obj = s3.get_object(
            Bucket=bucket_name,
            Key=file_name
        )
        return file_obj
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return None


def get_date_from_name(name):
    name = name.replace(".json", "")
    date_obj = datetime.strptime(name, "%Y%m%d%H%M%S")
    return date_obj.strftime("%Y-%m-%d %H:00:00")


def lambda_handler(event, context):

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    date_str = get_date_from_name(file_name)
    file_obj = get_file(file_name, bucket_name)

    if file_obj:
        file_content = file_obj['Body'].read().decode('utf-8')

        data = json.loads(file_content)

        points = []
        for point_data in data:
            points.append({
                "symbol": point_data['symbol'],
                "asset_type": "futures",
                "time_frame": "1h",
                "price": point_data['price'],
                "point_date": date_str,
            })

        requests.post(
            f'https://{host}/api/chart/point/bulk-points-without-chart/',
            json={
                'points': points
            },
            headers=app_headers
        )

    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }
