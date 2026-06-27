from django.conf import settings

from .nomba import NombaProvider


def get_payment_provider():
    provider = getattr(settings, "PAYMENT_PROVIDER", "nomba")
    providers = {
        "nomba": NombaProvider,
    }
    if provider not in providers:
        raise ValueError(f"Unknown payment provider: {provider}")
    return providers[provider]()
