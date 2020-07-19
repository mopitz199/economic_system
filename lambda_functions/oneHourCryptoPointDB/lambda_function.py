import json
import sentry_sdk
import os
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from oneHourCryptoPointDB.add_new_cryptos import run

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[AwsLambdaIntegration()]
)


def lambda_handler(event, context):
    run()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
