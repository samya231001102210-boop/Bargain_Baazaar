# Bargain Baazaar — Complete Full-Stack Project

React + Vite frontend and Python FastAPI backend with MongoDB Atlas.

## Project structure
- `frontend/` — React/Vite marketplace interface
- `backend/` — FastAPI APIs, MongoDB, auth, categories, listings, offers, orders, payments, reviews, wishlist, uploads and starter chat endpoints

## 1. Configure MongoDB Atlas
Open `backend/.env.example`, copy it to `backend/.env`, and fill in your Atlas connection string and a strong JWT secret. In Atlas, create a Database User and allow your current IP in Network Access. Never share or commit `.env`.

## 2. Start the backend (PowerShell terminal 1)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env before starting
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API docs: http://127.0.0.1:8000/docs

Seed starter categories in another backend terminal with the virtual environment active:
```powershell
python -m app.seeders.category_seeder
```

## 3. Start the frontend (PowerShell terminal 2)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173

## Current scope
The frontend includes marketplace browsing, category and listing filters, account registration/login, listing creation, and making offers. The backend includes the corresponding API foundations plus wishlist, reviews, orders, payment endpoints, uploads, admin summary and basic chat message endpoints.

Before production, finish and test private real-time Socket.IO authentication/delivery, full payment webhook and refund lifecycle, authorization rules for all resources, order fulfilment, email verification/password reset, rate limiting, audit logging, and frontend flows for seller/admin dashboards and order/payment management. Use Razorpay test credentials until payment testing is complete.
