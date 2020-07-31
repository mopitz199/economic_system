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
from oneHourETFPointFile1.etf import etf

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[AwsLambdaIntegration()]
)


def chunks(list_data, elements_per_chunk):
    """Yield successive n-sized chunks from list_data."""
    chunk_list = []
    for i in range(0, len(list_data), elements_per_chunk):
        chunk_list.append(list_data[i:i + elements_per_chunk])
    return chunk_list


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
        price = content.find('span', {'class': 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
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
    return date_obj.strftime("%Y%m%d%H0000_1")


def lambda_handler(event, context):

    first_part = math.ceil(len(etf)/float(3))
    chunks_list = chunks(etf, first_part)

    proxies = generate_proxies()

    result_values = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        for symbol in chunks_list[0]:
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
    s3.upload_file("/tmp/temp_data.json", "etf-listings-latest", f"{name}.json")

    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }
