"""
Domain exceptions for Vilapay.

The API layer catches these and maps them to appropriate HTTP responses.
Adding a new domain error: subclass VilapayError and add it here — no
changes needed anywhere else in the service layer.
"""


class VilapayError(Exception):
    """Base class for all domain errors."""


class GroupFullError(VilapayError):
    """All slots in the group are taken."""


class SlotTakenError(VilapayError):
    """The requested slot number is already occupied."""


class InvalidGroupStateError(VilapayError):
    """The operation is not allowed given the group's current status."""


class AlreadyPaidError(VilapayError):
    """The member has already made a completed contribution for this cycle."""


class InsufficientWalletBalance(VilapayError):
    """The save-ahead wallet balance is too low to cover the contribution."""


class PaymentProviderError(VilapayError):
    """The payment provider (Nomba) returned an error or is unreachable."""


class WebhookVerificationError(VilapayError):
    """The incoming webhook signature did not pass verification."""


class WalletLimitExceededError(VilapayError):
    """The user has reached the maximum number of Save-Ahead wallets for their tier."""
