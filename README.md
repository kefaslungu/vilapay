# VilaPay

> **Your village, your money, your turn.**

VilaPay digitizes the traditional Nigerian rotating savings system — ajo, esusu, adashi — and makes it trustless, automatic, and accessible to anyone with a smartphone.

---

## The Problem

Rotating savings groups (ajo/esusu) are one of the most widely practised forms of informal finance in Nigeria, yet they remain entirely manual. Organizers chase payments, members default, records are kept in notebooks or WhatsApp chats, and payouts depend on trust. When someone doesn't pay, the whole group suffers — and there is no recourse.

## The Solution

VilaPay replaces the manual process with an automated platform. Members authorize a one-time direct debit mandate through Nomba, and from that point the platform handles everything: collecting contributions on schedule, verifying payments via webhook, and sending payouts directly to the recipient's bank account — automatically, every cycle. No chasing. No defaults. No manual tracking.

---

## Key Features

- **Automated contribution collection** — Celery Beat triggers collection on each cycle date. Nomba executes the debit. No human intervention required.
- **Instant payouts** — Once all contributions are collected for a cycle, the full pot is transferred directly to the recipient's verified bank account via Nomba.
- **Group virtual accounts** — Each savings group gets a dedicated Nomba virtual account for transparent fund holding.
- **Direct debit mandates** — Members authorize automatic collection once. The platform debits them every cycle without requiring repeat action.
- **Save-ahead wallets** — Each member gets an isolated Nomba virtual account to pre-save funds before their contribution deadline, reducing the risk of missed collections.
- **Invite codes** — Group organizers share a unique code (e.g. `VLA-8K2QF9`) for members to join. No friction.
- **Immutable ledger** — Every deposit, withdrawal, payout, and refund is recorded as an audit entry. Full transparency for every group.
- **Webhook verification** — All Nomba payment events are verified using HMAC-SHA256+Base64 signatures before being processed.
- **Rate limiting** — Redis-backed rate limiting on all endpoints to prevent abuse.

---

## How It Works

```
1. Register & log in
2. Create a group  →  set name, slot count, contribution amount, frequency, and start date
3. Members join    →  via direct link or invite code
4. Activate        →  provisions a Nomba virtual account and generates the full payout schedule
5. Add bank account →  verified against Nomba in real time
6. Set up mandate  →  one-time direct debit authorization via Nomba
7. Sit back        →  contributions are collected automatically every cycle
8. Get paid        →  when it's your turn, the full pot lands in your bank account
```

---

## Live Demo

| Resource | URL |
|---|---|
| Web App | https://vilapay.ng |
| API Root | https://api.vilapay.ng/ |
| Interactive API Docs (Swagger) | https://api.vilapay.ng/v1/docs/ |
| API Schema | https://api.vilapay.ng/v1/schema/ |

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6, Django REST Framework |
| Database | PostgreSQL 16 |
| Cache & Queue | Redis 7, Celery 5, Celery Beat |
| Authentication | SimpleJWT (JWT access + refresh tokens) |
| Payments | Nomba API (virtual accounts, direct debit, bank transfers, webhooks) |
| API Docs | drf-spectacular (OpenAPI 3) |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 19, TypeScript |
| Build | Vite 8 |
| Styling | Tailwind CSS 4 |
| Routing | React Router 7 |
| State | Zustand 5 |
| Data Fetching | TanStack React Query 5, Axios |

### Infrastructure
| Layer | Technology |
|---|---|
| Server | Azure VM |
| Web Server | nginx + Gunicorn |
| SSL | Let's Encrypt |
| CI/CD | GitHub Actions (lint, security scan, auto-deploy) |
| Monitoring | Prometheus + Grafana |
| Security Scanning | Bandit, CodeQL |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/v1/auth/register/` | Register a new user |
| POST | `/v1/auth/login/` | Login — returns JWT access + refresh tokens |
| POST | `/v1/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/v1/auth/me/` | View or update profile |
| GET | `/v1/auth/banks/` | List supported banks |
| GET/POST | `/v1/auth/me/bank-accounts/` | Manage bank accounts |
| GET/POST | `/v1/groups/` | List or create savings groups |
| GET | `/v1/groups/{id}/` | Group detail |
| POST | `/v1/groups/{id}/join/` | Join a group |
| POST | `/v1/groups/join-by-code/` | Join a group using an invite code |
| POST | `/v1/groups/{id}/activate/` | Activate a full group |
| POST | `/v1/groups/{id}/cancel/` | Cancel a group |
| GET | `/v1/groups/{id}/members/` | List group members |
| GET | `/v1/groups/{id}/cycles/` | View payout cycle schedule |
| GET | `/v1/groups/memberships/` | Get all groups the current user belongs to |
| GET | `/v1/wallets/` | List save-ahead wallets |
| GET | `/v1/wallets/transactions/` | Unified contribution + payout history |
| GET | `/v1/wallets/{id}/ledger/` | Wallet transaction history |
| GET/POST | `/v1/payments/mandates/` | Manage direct debit mandates |
| GET | `/v1/payments/contributions/` | Contribution history |
| POST | `/v1/payments/webhooks/nomba/` | Nomba payment webhook (HMAC-verified) |
| GET | `/v1/payouts/` | Payout history |

Full interactive documentation is available at [api.vilapay.ng/v1/docs/](https://api.vilapay.ng/v1/docs/).

---

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

Or explore everything interactively at [api.vilapay.ng/v1/docs/](https://api.vilapay.ng/v1/docs/).

---

## Business Model

VilaPay operates on a freemium tier system:

| Tier | Target User | Limits |
|---|---|---|
| **Free** | Casual users | 1 save-ahead wallet |
| **Individual Pro** | Active savers | Up to 5 wallets, priority support |
| **Collector Pro** | Group organizers | Unlimited groups, advanced analytics |

Revenue comes from subscription fees on paid tiers and a small transaction fee on payouts processed through the platform.

---

## Local Development

```bash
git clone https://github.com/kefaslungu/vilapay.git
cd vilapay

# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt
cp .env.example .env  # fill in your values
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd src/frontend
npm install
npm run dev
```

---

## Security

- All endpoints protected with JWT authentication
- Nomba webhook payloads verified using HMAC-SHA256 + Base64
- Redis-backed rate limiting on all public endpoints
- Bandit and CodeQL security scanning in CI on every push
- SSL enforced in production via Let's Encrypt

---

*Built for the DevCareer × Nomba Hackathon 2026.*
