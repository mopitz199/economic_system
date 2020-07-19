import boto3
import concurrent.futures
import json
import math
import random
import requests
import time
import os

from bs4 import BeautifulSoup
from datetime import datetime
from quarterlyStockFinancialInfoFile2.stocks import stock_symbols as symbols

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
        url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
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


def get_value(symbol, proxy, date_str, tries=0):

    content = get_content(symbol, proxy)
    if not content:
        return None

    try:
        diluted_eps = content.find(
            'span',
            text='Diluted EPS'
        ).parent.findNext('td').text

        diluted_eps = diluted_eps.replace(",", "").strip()

        return {
            'symbol': symbol,
            'value': float(diluted_eps),
            'diluted_eps_date': date_str
        }
    except Exception:
        if tries < 7:
            time.sleep(2)
            return get_value(symbol, proxy, date_str, tries+1)
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


def lambda_handler(event, context):

    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    first_part = math.ceil(len(symbols)/float(10))
    chunks_list = chunks(symbols, first_part)

    proxies = generate_proxies()

    result_values = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        for symbol in chunks_list[1]:
            e = executor.submit(
                get_value,
                symbol,
                get_proxy(proxies),
                date_str
            )
            results.append(e)

        for f in concurrent.futures.as_completed(results):
            result = f.result()
            if result:
                result_values.append(result)

    s3 = boto3.client('s3')

    with open("/tmp/temp_data.json", "w") as f:
        json.dump(result_values, f)

    name = datetime.utcnow().strftime("%Y%m%d_2")
    s3.upload_file(
        "/tmp/temp_data.json",
        "stocks-financial-info-listings-latest", f"{name}.json"
    )

    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }
