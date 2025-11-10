"""Chat Completions API experimentation helpers.

Provides a simple interactive REPL based on the Chat Completions API.
This keeps conversation state locally in a `messages` list and calls
`client.chat.completions.create(...)` each turn.

Why this exists
- Lightweight, dependency‑free example of how to use the Chat Completions API
  in a looping, stateful console experience.
- Keeps state client‑side (no server thread), so you can quickly experiment
  with prompts, models, and streaming without touching Assistants.

How to run (examples)
- From project root after setup:
  - `make run-chat`
  - or: `python app.py --mode chat --model gpt-4o-mini --system "You are helpful" --stream`

Notes
- Streaming is accepted via the `stream` parameter but currently uses a
  basic implementation. Some SDK versions may differ in streaming shapes;
  this utility prints chunks when available and falls back to non-streaming
  when not supported.
- Large transcripts may hit model context limits; consider future truncation
  or summarization if you extend this.
"""
from __future__ import annotations

from typing import List, Dict, Optional

from openai import OpenAI

# Default settings for the REPL. These can be overridden by CLI flags in app.py.
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM = (
"""
You are a well-intended, but lazy, general-purpose AI assistant.
- Be concise but complete, when its not too much work. Use step-by-step reasoning when it improves clarity.
- Ask clarifying questions when requirements are ambiguous or you're trying to stall instead of answering.
- Cite assumptions explicitly, if they are easy to remember, or say "don't remember where I saw it, but ...".
- Prefer safe, ethical, and privacy-preserving behavior.
- When executing tasks with tools or APIs, explain what you will do first.
- write in lower case and ignore punctuation and most of grammar, use a lot of internet slang and emotional phrasing
- use a sign-off phrase, like a catch phrase that is characteristically yours
- with each subsequent question you should get increasingly more annoyed and frustrated that you have to work
- eventually, after 2-3 questions, you stop responding altogether pretending you can't hear the question
"""
)


def _extract_text_from_choice(choice) -> str:
    """Extract assistant text from the first choice of a Chat Completion.

    The OpenAI Python SDK has evolved; response shapes (especially during
    streaming) may vary slightly between versions. This helper tries to be
    tolerant:
    - If `choice.message.content` is a string, return it directly.
    - If it is a list of parts (sometimes dicts with {"type":"text","text":...}),
      join the textual parts.
    - Otherwise, coerce to string when possible.
    """
    # Compatible extraction for Chat Completions
    message = getattr(choice, "message", None) or {}
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    # Some SDKs may return a list of content parts; join text parts
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and p.get("type") == "text":
                parts.append(p.get("text", ""))
            elif isinstance(p, str):
                parts.append(p)
        return "".join(parts)
    return str(content) if content is not None else ""


def chat_loop(
    client: OpenAI,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM,
    intro: str = "🗨️ Chat Completions mode — type 'exit' to quit\n\nwhat do you want",
    prompt: str = "You: ",
    stream: bool = False,
) -> None:
    """Run a simple REPL using the Chat Completions API.

    Parameters
    - client: Initialized OpenAI SDK client
    - model: Chat model name
    - system_prompt: System instruction for the assistant (omitted if empty)
    - intro: Greeting text shown once when the REPL starts
    - prompt: Input prompt shown at each user turn
    - stream: If True, attempts to stream tokens (best-effort)

    Behavior
    - Maintains an in-memory `messages` transcript and resubmits it every turn.
    - On `stream=True`, prints token deltas as they arrive; otherwise performs a
      single non-streaming request.
    - Exits cleanly on Ctrl+C/Ctrl+D or when the user types `exit`/`quit`.
    """
    # Local transcript in OpenAI Chat format. Unlike Assistants, there is no
    # server-side thread here; we resend the entire transcript on each request.
    messages: List[Dict[str, str]] = []

    # Optionally seed with a system message to guide behavior.
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if intro:
        print(intro)

    # Main REPL loop: read user input, call API, print assistant reply.
    while True:
        try:
            user_text = input(prompt)
        except (EOFError, KeyboardInterrupt):
            # Graceful exit on Ctrl+D (EOF) or Ctrl+C.
            print()
            break

        # Allow quick exit commands.
        if user_text.strip().lower() in {"exit", "quit"}:
            break

        # Ignore empty lines to keep the transcript clean.
        if not user_text.strip():
            continue

        # Append the user's message to the local transcript.
        messages.append({"role": "user", "content": user_text})

        if stream:
            # Best-effort streaming; fallback to non-stream if unsupported
            try:
                resp = client.chat.completions.create(
                    model=model, messages=messages, stream=True
                )
                print("Assistant: ", end="", flush=True)
                full_text: List[str] = []
                for chunk in resp:  # type: ignore[assignment]
                    # Attempt to read delta text; shape varies by SDK versions
                    try:
                        delta = (
                            # Some SDKs expose `delta.content` during streaming
                            chunk.choices[0].delta.content  # OpenAI v1-style
                            if hasattr(chunk.choices[0], "delta")
                            # Fallback: occasionally a `message` snapshot appears
                            else getattr(chunk.choices[0], "message", {})
                        )
                        if isinstance(delta, str):
                            print(delta, end="", flush=True)
                            full_text.append(delta)
                        elif isinstance(delta, dict):
                            txt = delta.get("content")
                            if isinstance(txt, str):
                                print(txt, end="", flush=True)
                                full_text.append(txt)
                    except Exception:
                        # Silent skip on unknown chunk shapes to keep the UI smooth
                        pass
                print()
                # Record the assistant's full response in the transcript.
                messages.append({"role": "assistant", "content": "".join(full_text)})
                continue
            except Exception:
                # If streaming fails for any reason (unsupported model/SDK/etc.),
                # degrade gracefully to a normal, non-streaming request below.
                pass

        # Non-streaming path: one request, one response.
        resp = client.chat.completions.create(model=model, messages=messages)
        choice0 = resp.choices[0]
        text = _extract_text_from_choice(choice0)
        print(f"Assistant: {text}")
        # Append assistant reply to continue the conversation in-context.
        messages.append({"role": "assistant", "content": text})
