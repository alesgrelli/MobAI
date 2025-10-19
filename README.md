# MobAI — Mobile assistant prototype

This repository is a small prototype that demonstrates a mobile assistant built with:
- Flask (backend REST API)
- Kivy (mobile/desktop UI)

The focus is a simple, extensible architecture you can use for development and later package for Android/iOS.

## Project layout
- `backend/app.py` — Flask app and assistant provider plumbing (mock by default, optional OpenAI provider). Includes retry/backoff and concurrency throttling for OpenAI calls.
- `mobile/main_kivy.py` — Kivy UI: simple chat-style interface that posts messages to the backend and displays replies.
- `requirements.txt` — Python dependencies for development and tests.
- `scripts/` — PowerShell helpers to run the server, mobile client, and tests on Windows.
- `tests/` — pytest tests for backend endpoints.

## How it works (high level)
- The Kivy UI sends a POST /assist with JSON { "message": "..." } to the Flask backend.
- The backend selects an "assistant provider" based on the environment variable `ASSISTANT_PROVIDER`:
  - `mock` (default): `MockAssistant` provides deterministic replies for local dev and tests.
  - `openai`: `OpenAIAssistant` calls the OpenAI ChatCompletion API. The backend includes:
    - concurrency throttling (Semaphore) to limit simultaneous OpenAI requests,
    - retries with exponential backoff (via tenacity) on transient OpenAI errors,
    - environment-configurable `MAX_CONCURRENT` and `MAX_RETRIES`.

## Endpoints
- GET /ping
  - Returns JSON { "status": "ok", "message": "MobAI backend is running" }
- POST /assist
  - Request JSON: { "message": "Hello" }
  - Success response: { "reply": "..." }
  - Error cases:
    - 400: missing message
    - 500: assistant error or API failure

## Setup & run (Windows PowerShell)
1) Clone the repo and open a PowerShell terminal in the project root.

2) Create a virtual environment and install dependencies. You can use the provided scripts or the manual commands below.

Manual (recommended for clarity):

```powershell
# create venv
python -m venv .venv

# install dependencies into the venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3) Run the backend (mock provider by default):

```powershell
# run with mock provider (no external calls)
$env:ASSISTANT_PROVIDER = 'mock'
.\.venv\Scripts\python.exe backend\app.py
```

4) Run the Kivy UI in another terminal (desktop development):

```powershell
.\.venv\Scripts\python.exe mobile\main_kivy.py
```

5) Use OpenAI provider (optional):

```powershell
# only set these in your local session; don't check keys into source control
$env:ASSISTANT_PROVIDER = 'openai'
$env:OPENAI_API_KEY = '<YOUR_OPENAI_KEY>'
$env:MAX_CONCURRENT = '4'  # optional
$env:MAX_RETRIES = '4'    # optional
.\.venv\Scripts\python.exe backend\app.py
```

Important: Do not commit your API keys. Revoke and rotate any keys accidentally exposed.

## Tests
Run the pytest test suite (tests use the mock provider by default):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Configuration via environment variables
- `ASSISTANT_PROVIDER` — `mock` (default) or `openai`.
- `OPENAI_API_KEY` — required when `ASSISTANT_PROVIDER=openai`.
- `MAX_CONCURRENT` — maximum concurrent OpenAI calls (default: 4).
- `MAX_RETRIES` — maximum retry attempts for OpenAI transient failures (default: 4).

To keep envs local, consider using a `.env` file together with `python-dotenv` (I can add support if you want).

## Security & operational notes
- Never store API keys in source control. Use environment variables or a secrets manager.
- Monitor and set limits on usage and cost for your LLM provider.
- For production: add authentication, rate-limiting, logging, and metrics.

## Packaging for mobile
- For Android: use Buildozer (Linux recommended). Generate a `buildozer.spec` and follow Kivy/Buildozer docs.
- For iOS: packaging is more involved and typically requires macOS and toolchains that Kivy iOS provides.

If you want, I can scaffold a `buildozer.spec` and add packaging notes.

## Next steps I can help with
- Add `.env` support and a `.env.example` (no keys committed).
- Add a `/health` endpoint that reports the active provider and current concurrency settings.
- Add CI (GitHub Actions) to run linters and tests on push.
- Integrate OpenAI or another LLM more robustly (streaming responses, caching).

If you'd like one of these, tell me which and I'll implement it.
# MobAI — simple mobile assistant prototype

This repository contains a minimal Python prototype for a mobile assistant using a Flask backend and a Kivy-based UI that can run on desktop for development or be packaged for mobile.

Structure
- `backend/app.py` — Flask backend with two endpoints: `/ping` and `/assist` (simple echo logic).
- `mobile/main_kivy.py` — Kivy app that sends user messages to the backend and shows replies.
- `requirements.txt` — Python dependencies.
- `scripts/run_server.ps1` and `scripts/run_mobile.ps1` — PowerShell helper scripts for Windows.

Quick start (Windows PowerShell)

1) Create and activate virtualenv, install deps and run server:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; ./scripts/run_server.ps1
```

2) In another terminal, run the Kivy app:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; ./scripts/run_mobile.ps1
```

Notes
- The backend currently echoes the message. Replace the logic in `backend/app.py` with calls to your chosen assistant model or API.
- For real mobile deployment, use Buildozer (Android) or Kivy iOS tooling and follow their packaging guides. This README intentionally keeps desktop run simple for development.

Next steps
- Add authentication and rate limiting on the backend.
- Integrate a real LLM (OpenAI, local LLM) with streaming support.
- Add unit tests and CI.
