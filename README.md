# Vilapay

> Community rotating savings platform built on Nomba payment infrastructure.
> Your village, your money, your turn.

Vilapay digitizes the traditional Nigerian ajo/esusu: members join a rotating savings group, authorize a one-time direct debit mandate, and contributions are collected and payouts sent automatically every cycle — no chasing, no defaults, no manual tracking.

## Live API

| Resource | URL |
|---|---|
| API Root | https://api.vilapay.ng/ |
| Interactive Docs (Swagger) | https://api.vilapay.ng/v1/docs/ |
| API Schema | https://api.vilapay.ng/v1/schema/ |

The interactive docs at `/v1/docs/` allow you to explore and test every endpoint directly in the browser.

## Core Flow

1. **Register** — `POST /v1/auth/register/`
2. **Login** — `POST /v1/auth/login/` → receive JWT access + refresh tokens
3. **Create a group** — `POST /v1/groups/` with name, slot count, contribution amount, frequency, and start date
4. **Members join** — `POST /v1/groups/{id}/join/`
5. **Activate** — `POST /v1/groups/{id}/activate/` — provisions a Nomba virtual account for the group and generates the full payout cycle schedule
6. **Add bank account** — `POST /v1/auth/me/bank-accounts/` with bank code and account number (verified against Nomba)
7. **Set up direct debit mandate** — `POST /v1/payments/mandates/` — authorizes automatic contribution collection from the member's bank
8. **Contributions collected automatically** — Celery Beat triggers collection on each cycle date; Nomba webhooks confirm payment
9. **Payout** — once all contributions are collected for a cycle, the pot is transferred directly to the recipient's bank account

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/v1/auth/register/` | Register a new user |
| POST | `/v1/auth/login/` | Login, returns JWT tokens |
| POST | `/v1/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/v1/auth/me/` | View or update profile |
| GET | `/v1/auth/banks/` | List supported banks |
| GET/POST | `/v1/auth/me/bank-accounts/` | Manage bank accounts |
| GET/POST | `/v1/groups/` | List or create savings groups |
| GET | `/v1/groups/{id}/` | Group detail |
| POST | `/v1/groups/{id}/join/` | Join a group |
| POST | `/v1/groups/{id}/activate/` | Activate a full group |
| POST | `/v1/groups/{id}/cancel/` | Cancel a group |
| GET | `/v1/groups/{id}/members/` | List group members |
| GET | `/v1/groups/{id}/cycles/` | View payout cycle schedule |
| GET | `/v1/wallets/` | List save-ahead wallets |
| GET | `/v1/wallets/{id}/ledger/` | Wallet transaction history |
| GET/POST | `/v1/payments/mandates/` | Manage direct debit mandates |
| GET | `/v1/payments/contributions/` | Contribution history |
| POST | `/v1/payments/webhooks/nomba/` | Nomba payment webhook (HMAC-verified) |
| GET | `/v1/payouts/` | Payout history |

## Tech Stack

- **Backend**: Python 3.13, Django 6, Django REST Framework
- **Database**: PostgreSQL 16
- **Cache & Queue**: Redis 7, Celery, Celery Beat
- **Payments**: Nomba API (virtual accounts, direct debit, bank transfers, webhooks)
- **Infrastructure**: Azure VM, nginx, Gunicorn, Let's Encrypt SSL
- **CI/CD**: GitHub Actions (lint, security scan, automated deploy)
- **Monitoring**: Prometheus + Grafana

## Quick Test

```bash
# Register
curl -X POST https://api.vilapay.ng/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","full_name":"Your Name","phone_number":"+2348012345678","password":"YourPass@123"}'

# Login
curl -X POST https://api.vilapay.ng/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"YourPass@123"}'

# Create a group (use the access token from login)
curl -X POST https://api.vilapay.ng/v1/groups/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Ajo","slot_count":3,"contribution_amount":"5000.00","frequency":"monthly","start_date":"2026-08-01"}'
```

Or use the Swagger UI at https://api.vilapay.ng/v1/docs/ to test interactively.

## Local Development

```bash
git clone https://github.com/kefaslungu/vilapay.git
cd vilapay
python -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt
cp .env.example .env  # fill in your values
python manage.py migrate
python manage.py runserver
```
