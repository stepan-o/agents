"""Responses API experimentation helpers.

Provides a simple interactive REPL using the Responses API. It builds an
in-memory transcript and sends it as structured `input` per turn.

Notes
- Attempts streaming when `stream=True` using best-effort handling. SDKs may
  differ in event shapes; this tries common patterns and falls back safely.
- Keeps logic minimal and tool-free for experimentation.
"""
from __future__ import annotations

from typing import List, Dict

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM = (
    "You are a helpful, general-purpose AI assistant. Be concise but complete."
)


def _extract_text_from_response(resp) -> str:
    # Prefer the convenience property when available (OpenAI SDK v2+)
    txt = getattr(resp, "output_text", None)
    if isinstance(txt, str) and txt:
        return txt
    # Fallback traversal for older/alternate shapes
    try:
        out = getattr(resp, "output", None)
        if out and isinstance(out, list):
            for item in out:
                content = getattr(item, "content", None)
                if isinstance(content, list) and content:
                    first = content[0]
                    # text may be under first.text or first.get("text")
                    t = getattr(first, "text", None) or (
                        first.get("text") if isinstance(first, dict) else None
                    )
                    if isinstance(t, str):
                        return t
                    if isinstance(t, dict):
                        val = t.get("value")
                        if isinstance(val, str):
                            return val
    except Exception:
        pass
    return ""


def responses_loop(
    client: OpenAI,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM,
    intro: str = "🧰 Responses API mode — type 'exit' to quit",
    prompt: str = "You: ",
    stream: bool = False,
) -> None:
    """Run a simple REPL using the Responses API.

    Parameters
    - client: Initialized OpenAI SDK client
    - model: Model name
    - system_prompt: System instruction for the assistant
    - intro: Greeting text shown once
    - prompt: Input prompt shown each turn
    - stream: If True, attempts to stream tokens (best-effort)
    """
    transcript: List[Dict[str, str]] = []
    if system_prompt:
        transcript.append({"role": "system", "content": system_prompt})

    if intro:
        print(intro)

    while True:
        try:
            user_text = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_text.strip().lower() in {"exit", "quit"}:
            break
        if not user_text.strip():
            continue

        transcript.append({"role": "user", "content": user_text})

        if stream:
            try:
                stream_iter = client.responses.stream(
                    model=model,
                    input=transcript,
                )
                # The OpenAI SDK exposes an iterable of events
                print("Assistant: ", end="", flush=True)
                full = []
                for event in stream_iter:
                    # Best-effort: look for delta/text-like payloads
                    try:
                        if hasattr(event, "delta") and hasattr(event.delta, "text"):
                            piece = event.delta.text
                            if isinstance(piece, str):
                                print(piece, end="", flush=True)
                                full.append(piece)
                        elif hasattr(event, "data"):
                            data = event.data
                            part = getattr(data, "delta", None) or getattr(data, "text", None)
                            if isinstance(part, str):
                                print(part, end="", flush=True)
                                full.append(part)
                    except Exception:
                        pass
                print()
                transcript.append({"role": "assistant", "content": "".join(full)})
                continue
            except Exception:
                # Fall back to non-streaming
                pass

        resp = client.responses.create(model=model, input=transcript)
        text = _extract_text_from_response(resp)
        print(f"Assistant: {text}")
        transcript.append({"role": "assistant", "content": text})
