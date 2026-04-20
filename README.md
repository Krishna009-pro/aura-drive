# Aura Drive

Aura Drive is a cloud storage app built with FastAPI, SQLAlchemy, ImageKit, and a React/Vite frontend.

## Features

- JWT authentication with register and login
- Upload files to ImageKit
- Toggle assets between personal vault and community view
- Permanently delete assets from both the app and ImageKit

## Tech Stack

- Backend: FastAPI
- ORM: SQLAlchemy with `aiosqlite` or PostgreSQL
- Auth: FastAPI Users
- Media storage: ImageKit
- Frontend: React + Vite

## Project Structure

```bash
FastApi_Project/
├── app/
├── new_frontend/
├── Dockerfile
├── main.py
└── render.yaml
```

## Local Development

1. Install backend dependencies with `uv sync`.
2. Install frontend dependencies with `cd new_frontend && npm install`.
3. Start the backend with `uv run main.py`.
4. In another terminal, run `cd new_frontend && npm run dev`.

## Environment Variables

Create a `.env` file in the project root:

```ini
IMAGEKIT_PRIVATE_KEY=your_private_key
JWT_SECRET=your_secret_string
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

## Hosting

### Docker

Build and run:

```bash
docker build -t aura-drive .
docker run -p 8000:8000 --env-file .env aura-drive
```

### Render

This repo includes `render.yaml` for a one-click Render Blueprint.

1. Connect the GitHub repo in Render.
2. Choose the Blueprint option and let Render create the web service and PostgreSQL database.
3. Add `IMAGEKIT_PRIVATE_KEY`, `IMAGEKIT_PUBLIC_KEY`, and `IMAGEKIT_URL_ENDPOINT` in the Render dashboard.
4. Render will generate `JWT_SECRET` and wire `DATABASE_URL` automatically from the blueprint.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/jwt/login` | Obtain a JWT token |
| `POST` | `/auth/register` | Register a new account |
| `GET` | `/feed` | List assets |
| `POST` | `/uploadfile` | Upload a new asset |
| `PATCH` | `/posts/{id}/visibility` | Toggle community visibility |
| `DELETE` | `/posts/{id}` | Permanently delete an asset |
