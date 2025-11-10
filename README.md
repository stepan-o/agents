# openai-agents-starter

A minimal Python REPL app using the OpenAI Python SDK (Assistants/Threads/Runs). It provides a generic framework to define, connect to, and test OpenAI assistants (agents). Runtime logic lives in the local `agentkit/` package for clarity and extensibility.

## Quick start
- Recommended (existing uv environment):
  ```bash
  cp .env.example .env   # only for UV_PYTHON, do not store secrets here
  # Set UV_PYTHON to your interpreter path (discover one):
  uv run -n agents python -c "import sys; print(sys.executable)"
  make setup
  make run
  ```
- Or create a local venv automatically:
  ```bash
  make setup   # creates ./venv if missing and installs dependencies
  make run
  ```

Common tasks
```bash
make smoke   # offline smoke test
make python  # Python REPL in the selected env
make shell   # subshell in the selected env
make info    # print the interpreter path used by Make
```

## Environment
- `OPENAI_API_KEY` — your API key (set in your OS environment; don’t commit secrets).
- `UV_PYTHON` (optional) — full path to the Python interpreter of a uv‑managed env; put this in `.env` if you want Make to use it.

Examples
- macOS/Linux (current shell):
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```
- Windows PowerShell:
  ```powershell
  $Env:OPENAI_API_KEY = "sk-..."
  ```

## Run the app
```bash
make run
# or
python app.py --model gpt-4o-mini
```
The console starts a REPL. Type messages; type `exit` to quit.

## Smoke test (offline)
```bash
make smoke
```

## Architecture
- `app.py` — entrypoint; builds OpenAI client, constructs assistant/thread via `agentkit.builder`, starts REPL from `agentkit.repl`. Supports `--model`.
- `agentkit/`
  - `builder.py` — build the Assistant (Assistants API) and create a Thread. Central place to change model/instructions/name.
  - `repl.py` — minimal loop to send user messages and print replies.
  - `__init__.py` — re‑exports for convenience.

## Housekeeping
- Git ignore: a root `.gitignore` is provided; it ignores envs, caches, IDE files, and build artifacts. `uv.lock` stays tracked.
- Remove previously tracked build artifacts (if any):
  ```bash
  git rm -r --cached openai_agents_starter.egg-info || true
  git add -A && git commit -m "Untrack build artifacts per .gitignore"
  ```

## Troubleshooting (brief)
- “No interpreter found” → set `UV_PYTHON` in `.env` (see `.env.example`) or run `make setup` to create `./venv`.
- “ModuleNotFoundError” → `make setup` then `make smoke`.
- IDE uses wrong interpreter → point it to the path from `make info`.

## Notes
- Python compatibility: `pyproject.toml` declares `requires-python = ">=3.10"`.
- This project uses `requirements.txt` with `uv pip` by default. You can switch to `uv sync`/lockfile workflow later if you prefer.
