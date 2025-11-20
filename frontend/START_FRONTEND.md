# Starting the Frontend

To view the frontend, you need Node.js and npm installed.

## Install Node.js (if not already installed)

### Option 1: Using Homebrew (Recommended for macOS)
```bash
brew install node
```

### Option 2: Download from Node.js website
Visit https://nodejs.org/ and download the LTS version

### Option 3: Using nvm (Node Version Manager)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

## Start the Frontend Server

Once Node.js is installed:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: **http://localhost:3000**

The frontend will automatically proxy API requests to `http://localhost:8000` (where the backend should be running).
