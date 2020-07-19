import json
import os
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[AwsLambdaIntegration()]
)


def lambda_handler(event, context):
    dates = [
        datetime.today().strftime("%Y%m01"),
        datetime.today().strftime("%Y%m10"),
        datetime.today().strftime("%Y%m20"),
    ]

    for date_str in dates:
        time.sleep(7)
        url = f"https://coinmarketcap.com/historical/{date_str}/"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        trs = soup.findAll("tr", {"class": "cmc-table-row"})

        for tr in trs:
            td = tr.find("td", {"class": "cmc-table__cell--sort-by__rank"})
            ranking = int(td.find("div").text)

            td = tr.find("td", {"class": "cmc-table__cell--sort-by__symbol"})
            symbol = td.find("div").text

            td = tr.find("td", {"class": "cmc-table__cell--sort-by__name"})
            name = td.find("div").text
            slug = td.find("a")['href'].replace("/currencies/", "").replace("/", "")

            td = tr.find("td", {"class": "cmc-table__cell--sort-by__market-cap"})
            raw_marketcap = td.find("div").text
            raw_marketcap = raw_marketcap.replace("$", "")
            raw_marketcap = raw_marketcap.replace(".", "")
            raw_marketcap = raw_marketcap.replace(",", "")
            marketcap = int(raw_marketcap)

            td = tr.find("td", {"class": "cmc-table__cell--sort-by__price"})
            raw_price = td.find("a").text
            raw_price = raw_price.replace("$", "")
            raw_price = raw_price.replace(",", "")
            price = float(raw_price)

            headers = {
                'Authorization': "Token 26704736d3a5c8712dc149fb67643608f0397267",
                "Content-Type": "application/json"
            }

            date_obj = datetime.strptime(date_str, "%Y%m%d").date()
            date_str_body = date_obj.strftime("%Y-%m-%d")
            data = {
               "symbol": symbol,
               "ranking_date": date_str_body,
               "ranking": ranking,
               "marketcap": marketcap,
               "price": price,
               "slug": slug,
            }
            requests.post(
                'https://economicapp.io/api/rankings/create_ranking_from_symbol/',
                json=data,
                headers=headers
            )
    return {
        'statusCode': 200,
        'body': json.dumps("")
    }
