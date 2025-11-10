"""Simple REPL utilities for running an interactive session with an assistant."""
from __future__ import annotations

import time
from typing import Any
from openai import OpenAI  # SDK client class


def run_repl(
    client: OpenAI,
    thread: Any,
    *,
    assistant_id: str,
    intro: str = "Hello! Type 'exit' to quit.",
    prompt: str = "You: ",
) -> None:
    """Run a blocking REPL loop for the given thread using the provided client.

    Parameters
    - client: An initialized OpenAI SDK client object (from `openai import OpenAI`).
    - thread: A thread object returned by `client.threads.create()` identifying the conversation.
    - assistant_id: The assistant to run against this thread.
    - intro: Optional greeting printed once before the input loop starts.
    - prompt: The input prompt shown to the user for each turn.
    """
    if intro:
        print(intro)

    while True:
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower().strip() in {"exit", "quit", ":q"}:
            break

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

            # Simple polling loop
            while True:
                r = client.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if r.status in {"completed", "failed", "cancelled", "expired"}:
                    break
                time.sleep(0.5)

            if r.status != "completed":
                print(f"[Run status: {r.status}]")
            else:
                print_last_assistant_message(client, thread.id)
        except Exception as e:
            print("[ERROR running assistant]", e)


def print_last_assistant_message(client: OpenAI, thread_id: str) -> None:
    try:
        msgs = client.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in msgs.data:
            if getattr(m, "role", None) == "assistant":
                text = extract_text_from_message(m)
                if text:
                    print("Agent:", text)
                    return
        print("Agent: <no assistant message>")
    except Exception as e:
        print("[ERROR fetching messages]", e)


def extract_text_from_message(message: Any) -> str:
    # Try common data shapes conservatively
    try:
        parts = getattr(message, "content", None) or []
        if isinstance(parts, list) and parts:
            first = parts[0]
            # SDK may expose .text.value or nested fields
            if hasattr(first, "text") and hasattr(first.text, "value"):
                return first.text.value
            if isinstance(first, dict):
                return (
                    first.get("text", {}).get("value")
                    or first.get("text")
                    or first.get("value")
                    or ""
                )
    except Exception:
        pass
    try:
        return str(message)
    except Exception:
        return "<no output>"
