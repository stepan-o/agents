"""Simple testing harness to ask five fixed questions and print the dialogue.

This module provides a small, non-interactive runner that sends five
predefined questions to a model using one of the supported API modes and
prints the resulting dialogue in order.

Supported modes
- assistants: Uses Assistants/Threads/Runs (server-side thread)
- chat: Uses Chat Completions API (local transcript)
- responses: Uses Responses API (local transcript)

CLI usage examples
- python -m agentkit.harness --mode assistants --model gpt-4o-mini
- python -m agentkit.harness --mode chat --model gpt-4o-mini --system "You are helpful"
- python -m agentkit.harness --mode responses --model gpt-4o-mini --system "You are helpful"

Notes
- Requires OPENAI_API_KEY to be set in your OS environment.
- This harness is intentionally minimal: no streaming, no tools, no retries.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict, List

from openai import OpenAI

from .builder import AgentSpec, build_agent, create_session, DEFAULT_MODEL as ASSIST_DEFAULT_MODEL
from .chat_completions import DEFAULT_SYSTEM as CHAT_DEFAULT_SYSTEM, DEFAULT_MODEL as CHAT_DEFAULT_MODEL
from .responses_mode import DEFAULT_SYSTEM as RESP_DEFAULT_SYSTEM, DEFAULT_MODEL as RESP_DEFAULT_MODEL


QUESTIONS: List[str] = [
    "how many books there have been written through human history",
    "can't you just count them yourself?",
    "how many have you read yourself?",
    "which book do you like the most?",
    "which one would you recommend I read?",
]

# Defaults are sourced from the mode modules. By default this harness uses:
# - Assistants: builder.DEFAULT_INSTRUCTIONS (via AgentSpec()) and builder.DEFAULT_MODEL
# - Chat: chat_completions.DEFAULT_SYSTEM and chat_completions.DEFAULT_MODEL
# - Responses: responses_mode.DEFAULT_SYSTEM and responses_mode.DEFAULT_MODEL
# To override in code, pass explicit values to the run_* functions (see examples below).


def _print_turn(user: str, assistant: str) -> None:
    print(f"You: {user}")
    print(f"Assistant: {assistant}")
    print()


def run_five_chat(client: OpenAI, *, model: str | None = None, system_prompt: str | None = None) -> None:
    """Run the five-Q harness using the Chat Completions API.

    Defaults:
    - model → chat_completions.DEFAULT_MODEL
    - system_prompt → chat_completions.DEFAULT_SYSTEM

    To override in code, pass explicit values, e.g.:
    # run_five_chat(client, model="gpt-4o-mini", system_prompt="You are helpful")
    """
    messages: List[Dict[str, str]] = []
    sys_msg = CHAT_DEFAULT_SYSTEM if system_prompt is None else system_prompt
    if sys_msg:
        messages.append({"role": "system", "content": sys_msg})
    use_model = model or CHAT_DEFAULT_MODEL
    for q in QUESTIONS:
        messages.append({"role": "user", "content": q})
        resp = client.chat.completions.create(model=use_model, messages=messages)
        choice = resp.choices[0]
        # Robust extraction similar to chat_completions helper
        text = ""
        try:
            msg = getattr(choice, "message", None) or {}
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                parts: List[str] = []
                for p in content:
                    if isinstance(p, dict) and p.get("type") == "text":
                        parts.append(p.get("text", ""))
                    elif isinstance(p, str):
                        parts.append(p)
                text = "".join(parts)
        except Exception:
            pass
        if not text:
            text = "" if getattr(choice, "finish_reason", None) else str(choice)
        messages.append({"role": "assistant", "content": text})
        _print_turn(q, text)


def run_five_responses(client: OpenAI, *, model: str | None = None, system_prompt: str | None = None) -> None:
    """Run the five-Q harness using the Responses API.

    Defaults:
    - model → responses_mode.DEFAULT_MODEL
    - system_prompt → responses_mode.DEFAULT_SYSTEM

    To override in code, pass explicit values, e.g.:
    # run_five_responses(client, model="gpt-4o-mini", system_prompt="You are helpful")
    """
    transcript: List[Dict[str, str]] = []
    sys_msg = RESP_DEFAULT_SYSTEM if system_prompt is None else system_prompt
    if sys_msg:
        transcript.append({"role": "system", "content": sys_msg})
    use_model = model or RESP_DEFAULT_MODEL
    for q in QUESTIONS:
        transcript.append({"role": "user", "content": q})
        resp = client.responses.create(model=use_model, input=transcript)
        # Prefer resp.output_text if available
        text = getattr(resp, "output_text", None)
        if not isinstance(text, str) or not text:
            text = ""
            try:
                out = getattr(resp, "output", None)
                if out and isinstance(out, list):
                    for item in out:
                        content = getattr(item, "content", None)
                        if isinstance(content, list) and content:
                            first = content[0]
                            t = getattr(first, "text", None) or (
                                first.get("text") if isinstance(first, dict) else None
                            )
                            if isinstance(t, str):
                                text = t
                                break
                            if isinstance(t, dict):
                                val = t.get("value")
                                if isinstance(val, str):
                                    text = val
                                    break
            except Exception:
                pass
        transcript.append({"role": "assistant", "content": text})
        _print_turn(q, text)


def _wait_for_run(client: OpenAI, *, thread_id: str, run_id: str, timeout: float = 120.0) -> Any:
    start = time.monotonic()
    while True:
        r = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if getattr(r, "status", None) in {"completed", "failed", "cancelled", "expired"}:
            return r
        if (time.monotonic() - start) > timeout:
            return r
        time.sleep(0.5)


def _print_last_assistant_message(client: OpenAI, thread_id: str) -> str:
    try:
        msgs = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in getattr(msgs, "data", []) or []:
            if getattr(m, "role", None) == "assistant":
                # Extract text similar to repl.extract_text_from_message
                try:
                    parts = getattr(m, "content", None) or []
                    texts: List[str] = []
                    if isinstance(parts, list):
                        for p in parts:
                            if hasattr(p, "text") and hasattr(p.text, "value"):
                                v = p.text.value
                                if isinstance(v, str):
                                    texts.append(v)
                                    continue
                            if isinstance(p, dict):
                                t = p.get("text")
                                if isinstance(t, str):
                                    texts.append(t)
                                    continue
                                if isinstance(t, dict):
                                    v2 = t.get("value")
                                    if isinstance(v2, str):
                                        texts.append(v2)
                                        continue
                                v3 = p.get("value")
                                if isinstance(v3, str):
                                    texts.append(v3)
                                    continue
                    if texts:
                        return "".join(texts)
                except Exception:
                    pass
                return str(m)
    except Exception:
        return ""
    return ""


def run_five_assistants(client: OpenAI, *, model: str | None = None, system_prompt: str | None = None) -> None:
    """Run the five-Q harness using the Assistants/Threads/Runs APIs.

    Defaults:
    - model → builder.DEFAULT_MODEL
    - instructions → builder.DEFAULT_INSTRUCTIONS (via AgentSpec())

    To override in code, pass explicit values, e.g.:
    # run_five_assistants(client, model="gpt-4o-mini", system_prompt="You are helpful")
    """
    spec = AgentSpec()  # uses DEFAULT_MODEL and DEFAULT_INSTRUCTIONS by default
    if model:
        spec.model = model
    if system_prompt is not None:
        spec.instructions = system_prompt
    assistant = build_agent(client, spec)
    thread = create_session(client, assistant.id)
    for q in QUESTIONS:
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=q)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
        _wait_for_run(client, thread_id=thread.id, run_id=run.id)
        text = _print_last_assistant_message(client, thread.id) or ""
        _print_turn(q, text)


def run_five(client: OpenAI, *, mode: str, model: str | None = None, system_prompt: str | None = None) -> None:
    """Dispatcher to run the five-question harness in the selected mode.

    Defaults by mode (when parameters are None):
    - assistants → builder.DEFAULT_MODEL and builder.DEFAULT_INSTRUCTIONS
    - chat       → chat_completions.DEFAULT_MODEL and chat_completions.DEFAULT_SYSTEM
    - responses  → responses_mode.DEFAULT_MODEL and responses_mode.DEFAULT_SYSTEM
    """
    if mode == "assistants":
        run_five_assistants(
            client,
            model=model or ASSIST_DEFAULT_MODEL,
            system_prompt=system_prompt,
        )
    elif mode == "chat":
        run_five_chat(
            client,
            model=model or CHAT_DEFAULT_MODEL,
            system_prompt=system_prompt,
        )
    elif mode == "responses":
        run_five_responses(
            client,
            model=model or RESP_DEFAULT_MODEL,
            system_prompt=system_prompt,
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Five-question testing harness")
    p.add_argument("--mode", choices=["assistants", "chat", "responses"], default="assistants")
    p.add_argument("--model", help="Model name (default depends on mode)")
    p.add_argument("--system", help="Optional system prompt/instructions")
    return p.parse_args()


def _main() -> int:
    args = _parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set. API calls will fail.")
    client = OpenAI()
    try:
        run_five(client, mode=args.mode, model=args.model, system_prompt=args.system)
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 1


if __name__ == "__main__":
    sys.exit(_main())
