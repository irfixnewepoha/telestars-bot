from __future__ import annotations


class FragmentError(Exception):
    """Base Fragment integration error."""


class RecipientNotFound(FragmentError):
    pass


class InsufficientWalletBalance(FragmentError):
    pass


class SessionExpired(FragmentError):
    """Cookies / hash expired or invalid."""


class RateLimited(FragmentError):
    pass


class FragmentUnavailable(FragmentError):
    pass


class UnknownOutcome(FragmentError):
    """Could not determine whether the purchase succeeded after a crash."""
