# agentkit/ package

Purpose
- Organized place for assistant/agent-related code used by the application (module name: "agentkit").
- Lets you build reusable helpers, tools, or assistant definitions without cluttering the top-level app.

Is it required to run the app?
- Yes. The app imports from this package (agentkit.builder and agentkit.repl) to construct the assistant and run the REPL.

What are the files?
- builder.py — functions to construct the assistant and create a thread (OpenAI SDK). Contains AgentSpec, a small dataclass holding the assistant’s model, instructions, and name.
- repl.py — a small REPL loop utility used by app.py.
  - `run_repl(client, thread, *, assistant_id, intro="Hello! Type 'exit' to quit.", prompt="You: ")`
    - client: Initialized OpenAI SDK client (from `openai import OpenAI`). Used to call the Assistants/Threads/Runs APIs.
    - thread: Thread object returned by `client.threads.create()` identifying the conversation context.
    - assistant_id: The assistant to run against this thread.
    - intro: Greeting printed once before the loop. Set to "" to suppress.
    - prompt: Input prompt shown each turn. Defaults to "You: ".
- __init__.py — package marker with module overview and re-exports for convenience

How could I extend it?
- Add new modules for tools/utilities (e.g., tools/web.py) and import them from builder or repl as needed.
- Add additional assistant specs (e.g., subclass AgentSpec) and switch in app.py via CLI flags or config.

Notes
- This package is separate from the root app entrypoint but lives in the same repository for simplicity.
- Keeping it isolated makes refactoring and testing assistant utilities easier.
