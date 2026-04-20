# Aura Drive

Aura Drive is a FastAPI + React app for uploading, sharing, and managing files with ImageKit storage.

## Vercel deployment

Deploy this repository as **two separate Vercel projects**:

1. **Frontend project**
   - Root directory: `new_frontend`
   - Framework: Vite / React
   - Build command: `npm run build`
   - Output directory: `dist`
   - Environment variable:
     - `VITE_API_BASE_URL` = your backend Vercel project URL, for example `https://aura-drive-api.vercel.app`

2. **Backend project**
   - Root directory: repository root
   - Entry file: `index.py`
   - Framework: Python / FastAPI
   - Environment variables:
     - `DATABASE_URL` = a persistent PostgreSQL connection string
     - `IMAGEKIT_PRIVATE_KEY` = your ImageKit private key
     - `JWT_SECRET` = a long random secret

## Important hosting notes

- Do not use SQLite on Vercel for production data.
- The backend now fails fast on Vercel if `DATABASE_URL`, `JWT_SECRET`, or `IMAGEKIT_PRIVATE_KEY` is missing.
- The frontend must point to the backend through `VITE_API_BASE_URL`.
- If you want the frontend and backend on different Vercel projects, that is the expected setup for this repo.

## Local development

### Backend

```bash
uv run main.py
```

### Frontend

```bash
cd new_frontend
npm install
npm run dev
```

## Environment examples

- Copy `.env.example` to `.env` for backend development.
- Copy `new_frontend/.env.example` to `.env.local` or set the variable in Vercel for the frontend project.
