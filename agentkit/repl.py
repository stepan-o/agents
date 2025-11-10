"""Assistants-mode REPL utilities.

A small, blocking REPL (read–eval–print loop) for interacting with an
OpenAI Assistant using Threads/Runs. This module focuses on:
- Simplicity: minimal logic to add a user message, start a run, and wait.
- Robustness: tolerant parsing of assistant message shapes from the SDK.
- Clarity: inline documentation to make future changes straightforward.

How this differs from Chat/Responses modes
- Here, conversation state is kept server-side in a Thread. We only append
  the new user message each turn and trigger a Run for the Assistant to
  respond. In Chat/Responses modes, we keep a local transcript instead.

Usage (typical)
- Build assistant + thread (see `agentkit.builder`), then call `run_repl(...)`.
- Keyboard shortcuts: Ctrl+C/Ctrl+D to exit; or type `exit`/`quit`/`:q`.

Limitations
- No tools/function-calling UI is implemented here. If your assistant uses
  tools, the Assistant may still run them, but this REPL only prints the last
  assistant message after completion.
"""
from __future__ import annotations

import time
from typing import Any, Iterable, Optional
from openai import OpenAI  # SDK client class

# Terminal statuses for a Run in the Assistants API
_TERMINAL_STATUSES = {"completed", "failed", "cancelled", "expired"}


def _wait_for_run(
    client: OpenAI,
    *,
    thread_id: str,
    run_id: str,
    poll_interval: float = 0.5,
    timeout: Optional[float] = 120.0,
):
    """Poll the run until a terminal state and return the final run object.

    Uses `client.threads.runs.retrieve(...)` (correct endpoint) and supports a
    simple timeout to prevent indefinite waits.
    """
    start = time.monotonic()
    while True:
        r = client.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if getattr(r, "status", None) in _TERMINAL_STATUSES:
            return r
        if timeout is not None and (time.monotonic() - start) > timeout:
            return r  # return latest seen state; caller will treat as timeout
        time.sleep(poll_interval)


def run_repl(
    client: OpenAI,
    thread: Any,
    *,
    assistant_id: str,
    intro: str = "🤖 Assistants mode — type 'exit' to quit",
    prompt: str = "You: ",
) -> None:
    """Run a blocking REPL loop for the given thread using the provided client.

    Parameters
    - client: An initialized OpenAI SDK client object (from `openai import OpenAI`).
    - thread: A thread object returned by `client.threads.create()` identifying the conversation.
    - assistant_id: The assistant to run against this thread.
    - intro: Optional greeting printed once before the input loop starts.
    - prompt: The input prompt shown to the user for each turn.

    Behavior
    - Each turn: add the user message to the server-side Thread, create a Run,
      wait until it finishes, and print the last assistant message found.
    - Exits cleanly on Ctrl+C/Ctrl+D or when the user types `exit`/`quit`/`:q`.
    """
    if intro:
        print(intro)

    while True:
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        # Standard exit commands
        if user_input.lower().strip() in {"exit", "quit", ":q"}:
            break
        # Ignore empty inputs to keep the thread cleaner
        if not user_input.strip():
            continue

        # Add user message to the thread
        try:
            client.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input,
            )
        except Exception as e:
            print("[ERROR adding message]", e)
            continue

        # Create a run and poll until completion
        try:
            run = client.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
            )

            # Wait for a terminal status using the correct endpoint
            r = _wait_for_run(client, thread_id=thread.id, run_id=run.id)

            if getattr(r, "status", None) != "completed":
                # Print a brief diagnostic; callers can inspect the thread in the dashboard
                print(f"[Run status: {getattr(r, 'status', 'unknown')}]")
            else:
                print_last_assistant_message(client, thread.id)
        except Exception as e:
            print("[ERROR running assistant]", e)


def print_last_assistant_message(client: OpenAI, thread_id: str) -> None:
    """Fetch recent messages and print the most-recent assistant reply, if any."""
    try:
        msgs = client.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in getattr(msgs, "data", []) or []:
            if getattr(m, "role", None) == "assistant":
                text = extract_text_from_message(m)
                if text:
                    print("Assistant:", text)
                    return
        print("Assistant: <no assistant message>")
    except Exception as e:
        print("[ERROR fetching messages]", e)


def extract_text_from_message(message: Any) -> str:
    """Best-effort text extraction from an Assistants message object.

    Supports common shapes exposed by different SDK versions:
    - message.content as a list of parts; parts may expose `.text.value` or
      be dicts containing text and/or value fields. Concatenates multiple text
      parts when present.
    - Falls back to `str(message)` if no structured text is found.
    """
    try:
        parts = getattr(message, "content", None) or []
        texts: list[str] = []
        if isinstance(parts, list):
            for p in parts:
                # Newer SDKs: object with `.text.value`
                try:
                    if hasattr(p, "text") and hasattr(p.text, "value"):
                        val = p.text.value
                        if isinstance(val, str):
                            texts.append(val)
                            continue
                except Exception:
                    pass
                # Dict-like fallback
                if isinstance(p, dict):
                    # p.get("text") may be a str or a dict with {"value": str}
                    t = p.get("text")
                    if isinstance(t, str):
                        texts.append(t)
                        continue
                    if isinstance(t, dict):
                        v = t.get("value")
                        if isinstance(v, str):
                            texts.append(v)
                            continue
                    v2 = p.get("value")
                    if isinstance(v2, str):
                        texts.append(v2)
                        continue
        if texts:
            return "".join(texts)
    except Exception:
        pass
    try:
        return str(message)
    except Exception:
        return "<no output>"
