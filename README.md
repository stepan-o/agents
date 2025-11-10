# openai-agents-starter

A minimal Python REPL app using the OpenAI Python SDK supporting three experimentation modes: Assistants (Assistants/Threads/Runs), Chat Completions, and Responses API. Runtime logic lives in the local `agentkit/` package for clarity and extensibility.

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
make help    # show Make targets and parameterized usage examples
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
make run                # Assistants mode (default)
make run-chat           # Chat Completions mode
make run-responses      # Responses API mode

# Or with python directly
python app.py --mode assistants --model gpt-4o-mini
python app.py --mode chat --model gpt-4o-mini --system "You are helpful" --stream
python app.py --mode responses --model gpt-4o-mini --system "You are helpful" --stream
```
The console starts a REPL. Type messages; type `exit` to quit.

## Smoke test (offline)
```bash
make smoke
```

## Architecture
- `app.py` — entrypoint; builds OpenAI client and routes by `--mode`.
  - assistants: constructs assistant/thread via `agentkit.builder` and runs `agentkit.repl.run_repl`.
  - chat: runs `agentkit.chat_completions.chat_loop` (Chat Completions API).
  - responses: runs `agentkit.responses_mode.responses_loop` (Responses API).
- `agentkit/`
  - `builder.py` — build the Assistant (Assistants API) and create a Thread. Central place to change model/instructions/name.
  - `repl.py` — minimal loop to send user messages and print replies (Assistants mode).
  - `chat_completions.py` — REPL utilities for the Chat Completions API.
  - `responses_mode.py` — REPL utilities for the Responses API.
  - `__init__.py` — re‑exports convenience functions across modes.

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
