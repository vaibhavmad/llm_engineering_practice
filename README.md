# LLM Engineering — Hands-On Practice

Hands-on practice repo for **Ed Donner's LLM Engineering course**.
Every notebook and script is written by hand, one lesson at a time — **built to understand, not just to run.**

## How I work through it
- **Two-pass method:** watch the full lesson first, then code it along.
- **Unaided rebuilds:** for the harder flows, I re-build from scratch without the course files, to prove I own the concept (not just followed along).
- **Comments as a learning trail:** files are heavily commented with *what each step does and why* — so the repo doubles as my notes.

## Structure
- One folder per week — week_1/, week_2/, and so on.

## Setup
- Python version pinned in `.python-version`, environment managed with **uv**
- Install deps: `uv sync`  (from `pyproject.toml` / `uv.lock`)
- Create a `.env` with your API keys (e.g. `OPENAI_API_KEY`) — `.env` and local `.db` files are gitignored

## Note
This is course-practice code, built for learning. Some scripts expect API keys and local state, so they're meant to be read and run lesson-by-lesson rather than as one app.