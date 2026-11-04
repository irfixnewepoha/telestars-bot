from __future__ import annotations

from app.db.models import OrderStatus

# Allowed transitions. Any other transition raises InvalidTransitionError.
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.created: {
        OrderStatus.awaiting_payment,
        OrderStatus.cancelled,
        OrderStatus.paid,  # balance payment
    },
    OrderStatus.awaiting_payment: {
        OrderStatus.paid,
        OrderStatus.expired,
        OrderStatus.cancelled,
        OrderStatus.manual_review,
    },
    OrderStatus.paid: {
        OrderStatus.fulfilling,
        OrderStatus.manual_review,
        OrderStatus.failed_refunded,
    },
    OrderStatus.fulfilling: {
        OrderStatus.completed,
        OrderStatus.manual_review,
        OrderStatus.failed_refunded,
        OrderStatus.paid,  # retry after recoverable error before tx sent
    },
    OrderStatus.expired: {
        OrderStatus.manual_review,  # late payment → balance credit handled separately
    },
    # Terminal states have no outgoing transitions
    OrderStatus.completed: set(),
    OrderStatus.failed_refunded: set(),
    OrderStatus.manual_review: {
        OrderStatus.fulfilling,  # admin "retry"
        OrderStatus.completed,  # admin "confirm"
        OrderStatus.failed_refunded,  # admin "refund"
    },
    OrderStatus.cancelled: set(),
}


class InvalidTransitionError(Exception):
    def __init__(self, from_status: OrderStatus, to_status: OrderStatus) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Invalid order transition: {from_status.value} → {to_status.value}")


def assert_transition(from_status: OrderStatus, to_status: OrderStatus) -> None:
    allowed = ALLOWED_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise InvalidTransitionError(from_status, to_status)
