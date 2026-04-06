# 🌌 Aura Drive | Premium Cloud Storage

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

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.14+)
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
- Python 3.14 or higher
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
Create a `.env` file in the root directory with your ImageKit credentials:

```ini
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
```

### 4. Running the Server
Start the development server:

```bash
python main.py
```
The application will be available at [http://localhost:8000](http://localhost:8000).

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/jwt/login` | Obtain a JWT token | No |
| `POST` | `/auth/register` | Register a new account | No |
| `GET` | `/feed` | List all assets | Yes |
| `POST` | `/uploadfile` | Upload a new asset | Yes |
| `DELETE` | `/posts/{id}` | Delete an asset | Yes |

---

> [!NOTE]
> This project is designed for demonstration purposes. Ensure `SECRET` keys in `app/users.py` are moved to environment variables for production deployments.
