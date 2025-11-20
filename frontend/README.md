# Health Community Frontend

A React frontend for the Health Community platform - a Reddit-like forum for people with diseases to connect and share experiences.

## Features

- Browse condition-specific boards (Diabetes, Mental Health, Autoimmune, etc.)
- View posts from each condition board
- Create new posts to share experiences
- Clean, modern, and accessible UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Configuration

The frontend expects the backend API to be running at `http://localhost:8000` by default.

You can change this by creating a `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.
