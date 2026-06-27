from prometheus_client import Counter, Gauge, Histogram

payment_success = Counter(
    "vilapay_payment_success_total",
    "Total successful payments",
    ["payment_method", "tier"],
)

payment_failure = Counter(
    "vilapay_payment_failure_total", "Total failed payments", ["reason"]
)

payout_duration = Histogram(
    "vilapay_payout_duration_seconds",
    "Time to complete a payout",
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

active_groups = Gauge("vilapay_active_groups_total", "Number of active ajo groups")

webhook_processing_time = Histogram(
    "vilapay_webhook_processing_seconds", "Webhook processing duration", ["event_type"]
)

direct_debit_mandates = Counter(
    "vilapay_direct_debit_mandates_total",
    "Total direct debit mandates created",
    ["status"],
)

tier_upgrades = Counter(
    "vilapay_tier_upgrades_total", "Total tier upgrades", ["from_tier", "to_tier"]
)
