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
