# 🌌 Aura Drive | Premium Cloud Storage

![Aura Drive CI](https://github.com/Krishna009-pro/aura-drive/actions/workflows/ci.yml/badge.svg)

A sleek, high-performance cloud storage and image management platform built with **FastAPI**, **SQLAlchemy**, and **ImageKit.io**.

![Aura Drive UI Mockup](https://placehold.co/1200x600/0f172a/f8fafc?text=AURA+DRIVE+DASHBOARD)

## ✨ Features

- 🔐 **Secure Authentication**: Fully integrated JWT-based user system (Login/Register).
- ☁️ **Cloud Storage**: Seamless file uploads directly to ImageKit's global CDN.
- 🖼️ **Asset Management**: Organise your files with captions and track creation dates.
- ⚡ **Asynchronous Core**: Built on Python's `async/await` for maximum throughput.
- 💎 **Premium UI**: Modern dark-mode interface with glassmorphism and smooth animations.
- 🛡️ **Ownership Protection**: Users can only manage and delete their own uploaded assets.

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) with `aiosqlite`
- **Auth**: [FastAPI Users](https://fastapi-users.github.io/fastapi-users/)
- **Cloud Storage**: [ImageKit.io](https://imagekit.io/)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), and JavaScript (ES6+)

## 📁 Project Structure

```bash
FastApi_Project/
├── app/
│   ├── app.py          # Main FastAPI routes & logic
│   ├── db.py           # Database models & session management
│   ├── images.py       # ImageKit client configuration
│   ├── schema.py       # Pydantic data validation schemas
│   └── users.py        # Auth & User management config
├── static/
│   └── index.html      # Frontend UI (SPA)
├── main.py             # Server entry point
├── test.db             # SQLite database file
└── .env                # Environment variables (Internal)
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.12 or higher
- An [ImageKit.io](https://imagekit.io/) account

### 2. Architecture Deep Dive

Understanding how Aura Drive works under the hood:

- **The Flow**: 
  1. User selects a file in the **Frontend (Vanilla JS)**.
  2. JS sends a `FormData` request to the **FastAPI Backend**.
  3. FastAPI saves a temporary file, then streams it to **ImageKit Cloud**.
  4. Once uploaded, the Cloud URL is saved to **SQLite** via **SQLAlchemy**.
- **Asynchronous I/O**: Every part of the backend is `async`. This means while one user is waiting for a large 50MB upload to finish, the server can still process login requests for hundreds of other users simultaneously.
- **Glassmorphism Design**: The UI uses modern CSS `backdrop-filter` and `rgba` alpha-transparency to create a high-end, layered aesthetic that feels premium.

### 3. Installation
Clone the repository and install dependencies using `uv` (recommended) or `pip`:

```bash
# Using uv
uv sync

# Using pip
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory. You can use the provided `.env.example` as a template:

```ini
IMAGEKIT_PRIVATE_KEY=your_private_key
JWT_SECRET=your_secret_string
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### 4. Running Locally
Start the development server:

```bash
uv run main.py
```
The application will be available at [http://localhost:8000](http://localhost:8000).

## 🚀 Deployment Guide
Aura Drive is designed to be hosted on any platform that supports Docker or Python.

### 🐳 Deploying with Docker (Recommended)
The project includes a production-ready `Dockerfile`.

1. **Build the image**:
   ```bash
   docker build -t aura-drive .
   ```
2. **Run the container**:
   ```bash
   docker run -p 8000:8000 --env-file .env aura-drive
   ```

### ☁️ Cloud Hosting (Render)
Aura Drive is pre-configured for **Render** via the included `render.yaml` blueprint.

1. **Upload your code** to GitHub.
2. **On Render**, go to **Blueprints** and connect your repository.
3. Render will automatically provision:
   - A **FastAPI Web Service** (Dockerized).
   - A **Managed PostgreSQL** database.
4. Set the following **Environment Variables** in the Render dashboard:
   - `IMAGEKIT_PRIVATE_KEY`: Your private key from ImageKit.io.
   - `JWT_SECRET`: A long random string for auth security (Render will generate one if left blank).
   - `PORT`: 8000 (Set by default in the blueprint).

### ☁️ Other Platforms (Railway, Fly.io)
1. **Connect Repository**: Point your host to this GitHub repository.
2. **Set Environment Variables**: Add `IMAGEKIT_PRIVATE_KEY` and `JWT_SECRET`.
3. **Database**: Change the `DATABASE_URL` to your managed **PostgreSQL** instance connection string.


## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/jwt/login` | Obtain a JWT token | No |
| `POST` | `/auth/register` | Register a new account | No |
| `GET` | `/feed` | List all assets | Yes |
| `POST` | `/uploadfile` | Upload a new asset | Yes |
| `DELETE` | `/posts/{id}` | Delete an asset | Yes |

---

> [!TIP]
> Always use a dedicated PostgreSQL database and a strong `JWT_SECRET` for production deployments to ensure data persistence and security.
