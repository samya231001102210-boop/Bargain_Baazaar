# Bargain Baazaar — FastAPI Backend

Python FastAPI + MongoDB Atlas backend for the React/Vite Bargain Baazaar frontend.

## Requirements
- Python 3.11 or newer
- MongoDB Atlas account (or compatible MongoDB server)
- Git (optional)

## Windows PowerShell setup

From the project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set:
- `MONGODB_URI`: Atlas connection string. Replace DB_USER, DB_PASSWORD and YOUR_CLUSTER.
- `MONGODB_DATABASE`: leave as `bargain_baazaar`.
- `JWT_SECRET`: use a long random secret (at least 32 characters).
- `FRONTEND_URL`: `http://localhost:5173` for local Vite development.

If PowerShell blocks virtual-environment activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Start the API:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:
- API: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/health
- Swagger API docs: http://127.0.0.1:8000/docs

Seed categories (in a second terminal with the venv activated):
```powershell
python -m app.seeders.category_seeder
```

## Important first-run tasks
1. Register a normal user using `/api/auth/register`.
2. To create an administrator, manually change that user's `role` to `admin` in the Atlas `users` collection. Public registration intentionally cannot create admins.
3. Seed categories before creating listings.
4. Configure Razorpay test credentials before using payment endpoints.
5. Configure Cloudinary credentials before using image uploads.

## Main API endpoints
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/categories`, `POST /api/categories` (admin)
- `GET /api/listings`, `POST /api/listings`, `GET /api/listings/{id}`, `PATCH`, `DELETE`
- `POST /api/offers`, `GET /api/offers/mine`, `POST /api/offers/{id}/action`
- `GET/POST/DELETE /api/wishlist`
- `POST /api/reviews`, `GET /api/reviews/{listing_id}`
- `POST /api/orders`, `GET /api/orders/mine`
- `POST /api/payments/create-order/{order_id}`, `POST /api/payments/verify`
- `POST /api/chat/messages`, `GET /api/chat/{conversation_id}/messages`
- `GET /api/notifications`, `GET /api/admin/summary`
- `POST /api/uploads/image`

## Security and production notes
- Never commit `.env` or share secrets.
- Set Atlas Network Access to allow your development IP, preferably not `0.0.0.0/0`.
- Use Razorpay test mode until payment flows are fully tested.
- The Socket.IO server is a connection foundation only: add JWT handshake validation, participant authorization, rooms, message delivery and persistence events before enabling private real-time chat.
- Add email verification, password reset, rate limiting, audit logging, order fulfilment/refunds, inventory reservation and stricter review eligibility before production.
- This is a functional starter backend, not a production-audited payment or marketplace system.
