# agentkit/ package

Purpose
- Organized place for assistant/agent-related code used by the application (module name: "agentkit").
- Lets you build reusable helpers, tools, or assistant definitions without cluttering the top-level app.

Is it required to run the app?
- Yes. The app imports from this package to construct/run REPLs for multiple modes.

What are the files?
- builder.py — functions to construct the Assistant and create a Thread (Assistants API). Contains `AgentSpec` holding model, instructions, and name.
- repl.py — REPL loop for Assistants mode.
  - `run_repl(client, thread, *, assistant_id, intro="Hello! Type 'exit' to quit.", prompt="You: ")`
    - client: `OpenAI` client. Calls Assistants/Threads/Runs APIs.
    - thread: Conversation thread (`client.threads.create()`).
    - assistant_id: Target assistant id.
- chat_completions.py — REPL for Chat Completions API.
  - `chat_loop(client, model, system_prompt, intro, prompt, stream=False)`
    - Keeps messages locally; calls `client.chat.completions.create(...)`.
- responses_mode.py — REPL for Responses API.
  - `responses_loop(client, model, system_prompt, intro, prompt, stream=False)`
    - Sends a transcript as `input`; calls `client.responses.create(...)`.
- __init__.py — package marker with re-exports: `AgentSpec`, `build_agent`, `create_session`, `run_repl`, `chat_loop`, `responses_loop`.

How could I extend it?
- Add new modules for tools/utilities (e.g., tools/web.py) and import them from builder or repl as needed.
- Add additional agent specs or presets and switch in `app.py` via CLI flags or config.

Notes
- This package is separate from the root app entrypoint but lives in the same repository for simplicity.
- Keeping it isolated makes refactoring and testing assistant utilities easier.
