from __future__ import annotations

import pytest

from app.db.models import OrderStatus
from app.services.order_state import InvalidTransitionError, assert_transition


def test_valid_happy_path() -> None:
    assert_transition(OrderStatus.created, OrderStatus.awaiting_payment)
    assert_transition(OrderStatus.awaiting_payment, OrderStatus.paid)
    assert_transition(OrderStatus.paid, OrderStatus.fulfilling)
    assert_transition(OrderStatus.fulfilling, OrderStatus.completed)


def test_invalid_raises() -> None:
    with pytest.raises(InvalidTransitionError):
        assert_transition(OrderStatus.completed, OrderStatus.paid)
    with pytest.raises(InvalidTransitionError):
        assert_transition(OrderStatus.created, OrderStatus.completed)
