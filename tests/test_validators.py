from __future__ import annotations

from app.utils.validators import normalize_username, parse_stars_amount


def test_username_valid() -> None:
    assert normalize_username("@Durov") == "durov"
    assert normalize_username("test_user") == "test_user"


def test_username_invalid() -> None:
    assert normalize_username("1abc") is None
    assert normalize_username("ab") is None
    assert normalize_username("a" * 40) is None
    assert normalize_username("") is None


def test_stars_amount() -> None:
    assert parse_stars_amount("50", 50, 9999) == 50
    assert parse_stars_amount("100", 50, 9999) == 100
    assert parse_stars_amount("1e3", 50, 9999) is None
    assert parse_stars_amount("49", 50, 9999) is None
    assert parse_stars_amount("10000", 50, 9999) is None
    assert parse_stars_amount("abc", 50, 9999) is None
