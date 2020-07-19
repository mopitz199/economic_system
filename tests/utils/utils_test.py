from utils import get_performance


def test_get_performance_1():
    performance = get_performance(1, 2)
    assert performance == 100


def test_get_performance_2():
    performance = get_performance(-1, 2)
    assert performance == 300


def test_get_performance_3():
    performance = get_performance(10, -5)
    assert performance == -150


def test_get_performance_4():
    performance = get_performance(-20, -15)
    assert performance == 25


def test_get_performance_5():
    performance = get_performance(-10, -14)
    assert performance == -40


def test_get_performance_6():
    performance = get_performance(0, 5)
    assert performance is None


def test_get_performance_7():
    performance = get_performance(5, 0)
    assert performance == -100


def test_get_performance_8():
    performance = get_performance(-5, 0)
    assert performance == 100
