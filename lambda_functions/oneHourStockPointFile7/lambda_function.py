import boto3
import concurrent.futures
import json
import math
import random
import requests
import time
import os

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from oneHourStockPointFile7.stocks import stock_symbols as symbols

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[AwsLambdaIntegration()]
)


def get_content(symbol, proxy, tries=0):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}"
        if proxy:
            response = requests.get(url, proxies={"http": proxy})
        else:
            response = requests.get(url)

        content = BeautifulSoup(response.text, 'html.parser')
        return content
    except Exception:
        if tries < 7:
            time.sleep(2)
            return get_content(symbol, proxy, tries+1)
        else:
            print(symbol)
            return None


def get_price(symbol, proxy, tries=0):
    content = get_content(symbol, proxy)
    if not content:
        return None

    try:
        price = content.find('div', {'class': 'D(ib) Mend(20px)'}).findChildren("span")[0].text
        price = price.replace(",", "").strip()
        price = float(price)
        price = str(price)
        return {
            "price": price,
            "symbol": symbol,
        }
    except Exception:
        if tries < 7:
            time.sleep(2)
            return get_price(symbol, proxy, tries+1)
        else:
            print(symbol)
            return None


def generate_proxies(tries=0):
    try:
        response = requests.get("https://www.sslproxies.org/")
        content = BeautifulSoup(response.text, 'html.parser')
        table = content.find('table', {'id': 'proxylisttable'})
        tbody = table.find('tbody')
        trs = tbody.findAll('tr')

        proxies = []
        for tr in trs[:40]:
            tds = tr.findAll('td')
            proxy = f"{tds[0].text}:{tds[1].text}"
            proxies.append(proxy)
        return proxies
    except Exception:
        if tries < 7:
            time.sleep(2)
            return generate_proxies(tries+1)
        else:
            print("proxy fail")
            return []


def get_proxy(proxies):
    if proxies:
        return random.choice(proxies)
    else:
        return None


def get_date_name():
    date_obj = datetime.utcnow()
    minutes = date_obj.minute
    if minutes < 56:
        date_obj = date_obj - timedelta(hours=1)
    return date_obj.strftime("%Y%m%d%H0000_7")


def lambda_handler(event, context):

    proxies = generate_proxies()

    result_values = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        for symbol in symbols:
            e = executor.submit(get_price, symbol, get_proxy(proxies))
            results.append(e)

        for f in concurrent.futures.as_completed(results):
            result = f.result()
            if result:
                result_values.append(result)

    s3 = boto3.client('s3')

    with open("/tmp/temp_data.json", "w") as f:
        json.dump(result_values, f)

    name = get_date_name()
    s3.upload_file("/tmp/temp_data.json", "stocks-listings-latest", f"{name}.json")

    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }
