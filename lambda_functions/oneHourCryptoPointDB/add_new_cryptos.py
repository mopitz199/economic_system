import requests
import json
import boto3
import os
from datetime import datetime


coinmarketcap_headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ['COINMARKETCAP_PRO_API_KEY'],
}

app_headers = {
    'Authorization': 'Token '+os.environ['COINMARKETCAP_TOKEN'],
    'Content-Type': 'application/json'
}
host = '68.183.27.16:9000'
coinmarketcap_host = os.environ['COINMARKETCAP_HOST']

elements_per_chunk = 98


def _process_response(response):
    return json.loads(response.text)


def _chunks(list_data, elements_per_chunk):
    """Yield successive n-sized chunks from list_data."""
    for i in range(0, len(list_data), elements_per_chunk):
        yield list_data[i:i + elements_per_chunk]


def _get_coinmarketcap_ids():
    response = requests.get(
        f'http://{host}/api/asset/coinmarketcap-ids/',
        headers=app_headers
    )
    data = _process_response(response)
    ids = data['ids']
    return ids


def _build_create_asset_request(asset_data):
    website = asset_data['urls'].get('website', None)
    if website:
        website = website[0]

    technical_doc = asset_data['urls'].get('technical_doc', None)
    if technical_doc:
        technical_doc = technical_doc[0]

    twitter = asset_data['urls'].get('twitter', None)
    if twitter:
        twitter = twitter[0]

    reddit = asset_data['urls'].get('reddit', None)
    if reddit:
        reddit = reddit[0]

    announcement = asset_data['urls'].get('announcement', None)
    if announcement:
        announcement = announcement[0]

    chat = asset_data['urls'].get('chat', None)
    if chat:
        chat = chat[0]

    explorer = asset_data['urls'].get('explorer', None)
    if explorer:
        explorer = explorer[0]

    source_code = asset_data['urls'].get('source_code', None)
    if source_code:
        source_code = source_code[0]

    message_board = asset_data['urls'].get('message_board', None)
    if message_board:
        message_board = message_board[0]

    id = asset_data['id']
    symbol = asset_data.get('symbol', None)
    name = asset_data.get('name', None)
    logo = asset_data.get('logo', None)
    slug = asset_data.get('slug', None)
    description = asset_data.get('description', None)
    first_historical_data = asset_data.get('date_added', None)

    tags = asset_data.get('tags', None)
    if tags:
        tags = ",".join(tags)

    category = asset_data.get('category', None)

    return {
        "id": id,
        "symbol": symbol,
        "name": name,
        "slug": slug,
        "description": description,
        "logo": logo,
        "tags": tags,
        "category": category,
        "first_historical_data": first_historical_data,
        "chat": chat,
        "reddit": reddit,
        "twitter": twitter,
        "website": website,
        "explorer": explorer,
        "source_code": source_code,
        "announcement": announcement,
        "message_board": message_board,
        "technical_doc": technical_doc,
    }


def _get_coins_info(ids):
    ids = [str(id) for id in ids]
    ids = ",".join(ids)
    url = f'https://{coinmarketcap_host}/v1/cryptocurrency/info'
    parameters = {'id': ids}
    response = requests.get(
        url,
        params=parameters,
        headers=coinmarketcap_headers
    )
    data = _process_response(response)
    if 'data' in data:
        return data['data']
    else:
        return None


def _create_complete_crypto_asset(data):
    response = requests.post(
        f'http://{host}/api/asset/complete-crypto-asset/',
        json=data,
        headers=app_headers
    )
    return _process_response(response)


def _extract_ids(data):
    ids = []
    for coin_data in data:
        cryptomarket_id = coin_data['id']
        ids.append(cryptomarket_id)
    ids = [str(id) for id in ids]
    return ids


def _get_diff(list1, list2):
    id_lefts = list(set(list1) - set(list2))
    id_lefts = [str(id) for id in id_lefts]
    return id_lefts


def _create_chart(id):
    response = requests.post(
        f'http://{host}/api/chart/charts/',
        json={
            "asset": id,
            "time_frame": "1h",
            "chart_type": "point"
        },
        headers=app_headers
    )
    return _process_response(response)


def _create_charts(asset_ids):
    for id in asset_ids:
        _create_chart(id)


def _create_cryptos(data):
    ids = _extract_ids(data)

    current_ids = _get_coinmarketcap_ids()
    id_lefts = _get_diff(ids, current_ids)
    chunks_list = _chunks(id_lefts, elements_per_chunk)
    new_ids = []
    for chunk in chunks_list:
        coins_info = _get_coins_info(chunk)
        if coins_info:
            for cryptomarket_id in coins_info:
                coin_info = coins_info[cryptomarket_id]
                request = _build_create_asset_request(coin_info)
                new_asset = _create_complete_crypto_asset(request)
                new_ids.append(new_asset['id'])
    return new_ids


def _mapping_charts():
    response = requests.get(
        f'http://{host}/api/chart/charts/?limit=5000&chart_type=point&time_frame=1h&asset__asset_type=cryptos',
        headers=app_headers
    )
    chart_data = _process_response(response)
    mapping = {}
    for chart in chart_data['results']:
        symbol = chart['asset']['symbol']
        mapping[symbol] = chart['id']
    return mapping


def run():

    datetime_obj = datetime.utcnow().strftime("%Y-%m-%d %H:00:00")
    file_name = datetime.utcnow().strftime("%Y%m%d%H0000")

    s3 = boto3.client('s3')
    file_obj = s3.get_object(Bucket="cryptocurrency-listings-latest", Key=f"{file_name}.json")
    file_content = file_obj['Body'].read().decode('utf-8')

    data = json.loads(file_content)
    data = data['data']

    ids = _create_cryptos(data)
    _create_charts(ids)
    mapping = _mapping_charts()

    all_points = []
    for coin_data in data:
        symbol = coin_data['symbol']
        price = coin_data['quote']['USD']['price']
        chart_id = mapping.get(symbol, None)
        # volume = data['data'][coinmarketcap_id]['quote']['USD']['volume_24h']
        if price is None:
            continue

        if chart_id:
            point = {
                "chart": chart_id,
                "price": f"{round(price, 10)}",
                "source": "coinmarketcap",
                "point_date": datetime_obj
            }
        all_points.append(point)

    requests.post(
        f'http://{host}/api/chart/point/bulk-points/',
        json={
            'points': all_points
        },
        headers=app_headers
    )
