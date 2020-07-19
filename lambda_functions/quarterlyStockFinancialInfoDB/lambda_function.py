import json
import requests
import json
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
host = '68.183.27.16:9000'


def get_file(file_name, bucket_name):
    try:
        s3 = boto3.client('s3')
        file_obj = s3.get_object(
            Bucket=bucket_name,
            Key=file_name
        )
        return file_obj
    except Exception as e:
        print(e)
        return None


def lambda_handler(event, context):

    datetime_obj = datetime.utcnow().strftime("%Y-%m-%d")
    file_name = datetime.utcnow().strftime("%Y%m%d")

    for i in range(10):
        file_obj = get_file(
            f"{file_name}_{i+1}.json",
            "stocks-financial-info-listings-latest"
        )

        if file_obj:
            file_content = file_obj['Body'].read().decode('utf-8')

            data = json.loads(file_content)

            all_diluted_eps_data = []
            for diluted_eps_data in data:
                all_diluted_eps_data.append({
                    "symbol": diluted_eps_data['symbol'],
                    "value": diluted_eps_data['value'],
                    "diluted_eps_date": datetime_obj,
                })

            requests.post(
                f'http://{host}/api/stock/add-multiple-diluted-eps/',
                json={
                    'diluted_eps_data': all_diluted_eps_data
                },
                headers=app_headers
            )

    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }
