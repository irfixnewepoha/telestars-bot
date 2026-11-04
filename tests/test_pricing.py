from __future__ import annotations

from app.services.pricing import calc_client_price


def test_calc_rounds_up() -> None:
    # 1 TON = 500 RUB, 50 stars * 0.015 TON = 0.75 TON = 375 RUB = 37500 kop
    cost_nano = 750_000_000  # 0.75 TON
    price = calc_client_price(
        cost_ton_nano=cost_nano,
        ton_rub=500.0,
        markup_percent=10,
        platega_fee_percent=0,
        min_margin_kop=0,
    )
    # 37500 * 1.1 = 41250
    assert price == 41250


def test_min_margin() -> None:
    cost_nano = 10_000_000  # 0.01 TON
    price = calc_client_price(
        cost_ton_nano=cost_nano,
        ton_rub=100.0,  # cost = 1 RUB = 100 kop
        markup_percent=0,
        platega_fee_percent=0,
        min_margin_kop=500,
    )
    assert price >= 600  # 100 + 500


def test_fee_applied() -> None:
    cost_nano = 1_000_000_000  # 1 TON
    price = calc_client_price(
        cost_ton_nano=cost_nano,
        ton_rub=100.0,  # 10000 kop
        markup_percent=0,
        platega_fee_percent=10,
        min_margin_kop=0,
    )
    assert price == 11000
