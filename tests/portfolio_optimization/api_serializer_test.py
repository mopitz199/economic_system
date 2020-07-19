from apps.portfolio_optimization.api_serializers import (
    RequestOptimizationSerializer,
)


def test_request_optimization_serializer_1():
    data = {
        'optimism': 100,
        'total_amount_to_invest': 1000,
        'min_disposed_to_lose': 80,
        'asset_optimizations': [
            {
                'asset_id': 1,
                'min_to_invest': 10,
                'max_to_invest': 50,
                'amount_to_invest': 200
            }
        ]
    }
    serializer = RequestOptimizationSerializer(data=data)
    assert serializer.is_valid()


def test_request_optimization_serializer_2():
    data = {
        'optimism': 100,
        'min_disposed_to_lose': 80,
        'asset_optimizations': [
            {
                'asset_id': 1,
                'min_to_invest': 10,
                'max_to_invest': 50,
                'amount_to_invest': 200,
            }
        ]
    }
    serializer = RequestOptimizationSerializer(data=data)
    assert not serializer.is_valid()


def test_request_optimization_serializer_3():
    data = {
        'asset_optimizations': [
            {
                'asset_id': 1,
                'min_to_invest': 10,
                'max_to_invest': 50,
            }
        ]
    }
    serializer = RequestOptimizationSerializer(data=data)
    assert not serializer.is_valid()


def test_request_optimization_serializer_4():
    data = {
        'optimism': 100,
        'asset_optimizations': [
            {
                'asset_id': 1,
                'min_to_invest': 10,
                'max_to_invest': 50,
                'amount_to_invest': 200,
            }
        ]
    }
    serializer = RequestOptimizationSerializer(data=data)
    assert not serializer.is_valid()


def test_request_optimization_serializer_5():
    data = {
        'optimism': 100,
        'min_disposed_to_lose': 80,
        'asset_optimizations': [
            {
                'asset_id': 1,
                'min_to_invest': 10,
                'max_to_invest': 50,
            }
        ]
    }
    serializer = RequestOptimizationSerializer(data=data)
    assert serializer.is_valid()
