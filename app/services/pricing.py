from __future__ import annotations

import math
from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True, slots=True)
class PriceResult:
    price_kop: int
    cost_ton_nano: int
    ton_rub: float
    markup_percent: float


def calc_client_price(
    *,
    cost_ton_nano: int,
    ton_rub: float,
    markup_percent: float,
    platega_fee_percent: float,
    min_margin_kop: int,
) -> int:
    """
    Client price in kopecks, rounded UP.
    cost = ton_nano / 1e9 * ton_rub * 100 (kop)
    then apply markup + payment fee, enforce min margin.
    """
    cost_rub = (cost_ton_nano / 1_000_000_000) * ton_rub
    cost_kop = cost_rub * 100
    with_markup = cost_kop * (1 + markup_percent / 100)
    with_fee = with_markup * (1 + platega_fee_percent / 100)
    price = math.ceil(with_fee)
    # Ensure at least cost + min_margin
    min_price = math.ceil(cost_kop) + min_margin_kop
    return max(price, min_price)


def build_price(
    settings: Settings,
    cost_ton_nano: int,
    ton_rub: float,
) -> PriceResult:
    price_kop = calc_client_price(
        cost_ton_nano=cost_ton_nano,
        ton_rub=ton_rub,
        markup_percent=settings.markup_percent,
        platega_fee_percent=settings.platega_fee_percent,
        min_margin_kop=settings.min_margin_kop,
    )
    return PriceResult(
        price_kop=price_kop,
        cost_ton_nano=cost_ton_nano,
        ton_rub=ton_rub,
        markup_percent=settings.markup_percent,
    )
