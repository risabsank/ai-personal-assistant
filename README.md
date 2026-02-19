# AI Personal Assistant

A full-stack personal assistant application with a React chat interface and a FastAPI backend that can route requests to deterministic Google Workspace tools (Calendar and Gmail) or to an OpenAI-powered agent for multi-step reasoning.

---

## Table of Contents

- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [1) Clone and Install](#1-clone-and-install)
- [2) Configure Environment Variables](#2-configure-environment-variables)
- [3) Configure Google API Credentials](#3-configure-google-api-credentials)
- [4) Run the Backend](#4-run-the-backend)
- [5) Run the Frontend](#5-run-the-frontend)
- [How It Works End-to-End](#how-it-works-end-to-end)
- [API Contract](#api-contract)
- [Google OAuth Scopes Used](#google-oauth-scopes-used)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)
- [Suggested Improvements](#suggested-improvements)
- [License](#license)

---

## Overview

This repository contains an **AI Executive Assistant** with:

- A **frontend** (React + Vite + TypeScript) that provides a chat-style UI.
- A **backend** (FastAPI + Python) that:
  - Accepts user requests via `/chat`.
  - Applies deterministic intent routing for common requests.
  - Falls back to an LLM agent for tool-driven workflows.
  - Integrates with Google Calendar and Gmail APIs through OAuth credentials.

The current implementation is optimized for local development and experimentation.

---

## Core Capabilities

The backend supports tool calls for:

- Getting tomorrow's calendar events.
- Finding available time slots tomorrow.
- Scheduling meetings.
- Listing unread emails.
- Listing unread emails from a specific sender.
- Sending email.

The frontend displays a modern assistant-style conversation view with loading feedback and incremental message history.

---

## Architecture

```text
[React Frontend]
  └─ POST /chat (http://localhost:8000/chat)
          |
          v
    [FastAPI Backend]
      ├─ Intent router (keyword-based)
      │    ├─ Calendar tools
      │    └─ Gmail tools
      └─ LLM agent fallback (OpenAI tool-calling loop)
               ├─ Calendar tool functions
               └─ Gmail tool functions
```

Request flow:

1. User sends a message from the frontend.
2. Backend routes the request via `route_intent` for deterministic paths.
3. If no direct route matches, the backend calls `run_agent`.
4. The agent can invoke registered tools using OpenAI tool-calling.
5. Backend returns a plain response string to the frontend.

---

## Project Structure

```text
ai-personal-assistant/
├─ backend/
│  ├─ main.py                # FastAPI app and /chat endpoint
│  ├─ agent/
│  │  ├─ agent.py            # LLM loop + tool execution
│  │  ├─ config.py           # OpenAI client + model + tool schema
│  │  ├─ memory.py           # In-memory conversation state
│  │  └─ router.py           # Keyword-based intent router
│  └─ api/
│     ├─ google_auth.py      # OAuth token bootstrap and refresh
│     ├─ calendar_api.py     # Calendar read/write operations
│     ├─ gmail_api.py        # Gmail read/write operations
│     └─ tools.py            # Tool wrappers + formatter helpers
└─ frontend/
   ├─ src/App.tsx            # Chat UI
   ├─ src/api.ts             # Backend API request helper
   └─ package.json           # Frontend scripts/dependencies
```

---

## Technology Stack

### Frontend

- React 19
- TypeScript
- Vite
- ESLint

### Backend

- Python 3.10+
- FastAPI
- Uvicorn
- OpenAI Python SDK
- Google API Client
- Google OAuth libraries
- `python-dateutil`

---

## Prerequisites

Before running locally, install:

- **Node.js** 18+ and npm.
- **Python** 3.10+.
- A Google Cloud project with **Gmail API** and **Google Calendar API** enabled.
- An OpenAI API key with access to chat completions.

---

## 1) Clone and Install

### Clone

```bash
git clone <your-repo-url>
cd ai-personal-assistant
```

### Backend dependencies

Create and activate a virtual environment, then install required packages:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn openai google-api-python-client google-auth google-auth-oauthlib python-dateutil
```

### Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 2) Configure Environment Variables

Set your OpenAI key before starting the backend:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

(Optional) Add this to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

---

## 3) Configure Google API Credentials

The backend expects OAuth files in the project root:

- `credentials.json` (Google OAuth client credentials)
- `token.json` (generated on first successful login)

### Steps

1. In Google Cloud Console:
   - Enable **Google Calendar API** and **Gmail API**.
   - Create an **OAuth 2.0 Client ID** for a desktop app.
2. Download the OAuth client file and rename it to `credentials.json`.
3. Place `credentials.json` in the repository root.
4. Run a backend flow that triggers Google auth; this creates `token.json`.

> Keep both files out of version control and never commit real secrets.

---

## 4) Run the Backend

From the repository root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`.

---

## 5) Run the Frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

Vite usually serves at `http://localhost:5173`.

---

## How It Works End-to-End

- Frontend `sendMessage()` posts `{ message: string }` to `/chat`.
- Backend checks deterministic intent patterns first (e.g., "free slot", "unread email").
- For broader requests, backend falls back to the agent loop.
- Agent can call declared tools and then produce a final assistant reply.

This design gives you predictable responses for common tasks while still allowing flexible natural-language handling.

---

## API Contract

### `POST /chat`

**Request**

```json
{
  "message": "What meetings do I have tomorrow?"
}
```

**Response**

```json
{
  "response": "Tomorrow's schedule:\n1. ..."
}
```

---

## Google OAuth Scopes Used

The app currently requests:

- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/gmail.send`

Review and reduce scopes if you need stricter least-privilege behavior.

---

## Development Notes

- Conversation memory is currently in-process and non-persistent.
- Tool wrappers return human-readable formatted strings for deterministic routes.
- Frontend API URL is hardcoded to `http://localhost:8000/chat` in `frontend/src/api.ts`.

---

## Troubleshooting

### Backend import errors

If you see Python import path issues, run from repository root and verify your module paths and `PYTHONPATH`. Some imports currently assume specific module resolution behavior.

### Google OAuth issues

- Ensure `credentials.json` exists in project root.
- Delete stale `token.json` and re-authenticate if token refresh fails.
- Confirm OAuth consent and test user configuration in Google Cloud.

### CORS / connection problems

If frontend cannot connect to backend, verify:

- Backend is running on port `8000`.
- Frontend is using the expected URL in `frontend/src/api.ts`.
- FastAPI CORS middleware is configured if browser-origin restrictions appear.

---

## Suggested Improvements

- Add a backend `requirements.txt` or `pyproject.toml` for reproducible Python installs.
- Add `.env` loading support for local environment management.
- Add unit/integration tests for tools and routing.
- Add persistent storage for conversation memory.
- Centralize backend imports into package-safe absolute paths.
- Add Dockerfiles and `docker-compose` for one-command startup.

---

## License

No license file is currently defined in this repository. Add a `LICENSE` file (for example, MIT, Apache-2.0, or proprietary) before public distribution.
