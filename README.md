# CS411 - LEN PROJECT

## 1. Project Description 

LEN is a web-based platform designed to alleviate loneliness and improve mental well-being among patient communities by creating digital support groups. The platform enables patients with similar conditions and backgrounds to connect, share experiences, and provide mutual encouragement, fostering a sense of belonging and reducing feelings of isolation. This is transformative because it will enable scalable peer-to-peer patient support, which is currently a large issue for hospitals and other caretakers.

## 2. INSTALLATION AND RUNNING INSTRUCTIONS

### Prerequisites

- **Python 3.10+** (recommended)
- **Node.js 18+** and **npm**
- (macOS users: install with Homebrew, nvm, or from [nodejs.org](https://nodejs.org/))

### 1. Install Python dependencies

Open a terminal in the project root and run:

```bash
pip install -r requirements.txt
```

### 2. Start the Backend (API server)

In the project root, run:

```bash
uvicorn app.main:app --reload
```

- The backend will start at `http://localhost:8000`
- The database will be created automatically as `len_dev.db` (SQLite)

### 3. Start the Frontend

Open a second terminal, then:

```bash
cd frontend
npm install
npm run dev
```

- The frontend will be available at `http://localhost:3000`
- It will proxy API requests to the backend at `http://localhost:8000`

### 4. Access the Application

- Visit `http://localhost:3000` in your browser.
- You must log in, and you may either create a **user** account, using the sign-up functionality, or log in with an admin account with the username "mod@len.com" and password "lenmoderator1".

### Notes

- The backend will auto-create tables and seed initial boards and a guest user if none exist.
- For development, both servers must be running simultaneously.
- For troubleshooting Node.js or Python installation, see `frontend/START_FRONTEND.md`.

### Unit Tests

- To run the python unit tests, use the terminal and run 

```
pytest --cov=app --cov-report=term-missing
```