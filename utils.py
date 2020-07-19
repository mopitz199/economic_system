import datetime
import calendar
import math
from decimal import Decimal

from currency_converter import CurrencyConverter


def chunks(list_data, elements_per_chunk):
    """Yield successive n-sized chunks from list_data."""
    for i in range(0, len(list_data), elements_per_chunk):
        yield list_data[i:i + elements_per_chunk]


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(
        source_date.day,
        calendar.monthrange(year, month)[1]
    )
    return datetime.datetime.combine(
        datetime.date(year, month, day),
        source_date.time(),
    )


def add_years(source_date, years):
    day = source_date.day
    month = source_date.month
    year = source_date.year

    return datetime.datetime.combine(
        datetime.date(year+years, month, day),
        source_date.time(),
    )


def strip_zeros(number: Decimal) -> Decimal:
    try:
        integer_part = str(number).split(".")[0]
        decimal_part = str(number).split(".")[1]
        decimal_part = decimal_part.rstrip("0")
        if decimal_part:
            return Decimal(f'{integer_part}.{decimal_part}')
        else:
            return Decimal(f'{integer_part}')
    except Exception:
        return number


def round_price(number: Decimal) -> Decimal:
    number = Decimal(number)
    integer_part = str((math.modf(number)[1]))
    max_decimals = 7
    new_decimals = max_decimals - len(integer_part)

    decimal_str = '.'
    for i in range(new_decimals):
        decimal_str += '0'
    decimal_str += '1'
    return Decimal(number.quantize(Decimal(decimal_str)))


def num_integer_part(number):
    """Get the number of digit of the integer part of a number"""
    number = str(float(number))
    integer_part = number.split(".")[0]
    return len(integer_part)


def price_to_show(number: Decimal) -> Decimal:
    number = round_price(number)
    number = strip_zeros(number)
    return number


def to_usd(amount, currency):
    if currency != 'USD':
        currency_converter = CurrencyConverter()
        return Decimal(currency_converter.convert(amount, currency, 'USD'))
    else:
        return Decimal(amount)


def get_performance(init_value, ending_value):
    if init_value < 0 and ending_value > 0:
        percentage = (abs(ending_value/init_value)*100)+100
        return round(percentage, 2)
    elif init_value > 0 and ending_value < 0:
        percentage = ((abs(ending_value/init_value)*100)+100)*-1
        return round(percentage, 2)
    elif init_value > 0 and ending_value > 0:
        percentage = abs((ending_value*100)/init_value)
        return round(float((percentage - 100)), 2)
    elif init_value < ending_value < 0:
        percentage = 100-(abs(ending_value/init_value)*100)
        return round(percentage, 2)
    elif ending_value < init_value < 0:
        percentage = 100-(abs(ending_value/init_value)*100)
        return round(percentage, 2)
    elif init_value > 0 and ending_value == 0:
        return -100
    elif init_value < 0 and ending_value == 0:
        return 100
    else:
        return None


def str_to_datetime(str_date):
    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y"
        )
    except Exception:
        pass

    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y-%m"
        )
    except Exception:
        pass

    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y-%m-%d"
        )
    except Exception:
        pass

    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y-%m-%d %H"
        )
    except Exception:
        pass

    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y-%m-%d %H:%M"
        )
    except Exception:
        pass

    try:
        return datetime.datetime.strptime(
            str_date,
            "%Y-%m-%d %H:%M:%S"
        )
    except Exception:
        raise Exception(f'{str_date} format not found')
