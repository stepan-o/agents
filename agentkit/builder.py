"""Builder utilities for constructing a generic OpenAI Assistant (agent) and thread.

This module centralizes all OpenAI SDK interactions needed to:
- create the Assistant (Agents/Assistants API)
- create a Thread (conversation context) for interacting with that assistant

By keeping this logic here, the rest of the app (CLI/REPL, tools, tests)
can stay decoupled from SDK details, making future changes (e.g., model,
instructions, provider) more localized.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
# Note: OpenAI here refers to the Python SDK client class exported by the
# `openai` package. Constructing `OpenAI(...)` creates a client object used to
# call APIs (e.g., `client.assistants`, `client.threads`). Creating the
# client does not make a network request by itself; network calls happen when
# you invoke its methods.


DEFAULT_MODEL = "gpt-4o-mini"

DEFAULT_INSTRUCTIONS = (
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
).strip()


@dataclass
class AgentSpec:
    """Lightweight configuration object for building an Assistant.

    Fields
    - model: Model identifier to use for the Assistant (defaults to DEFAULT_MODEL).
    - instructions: System prompt/instructions given to the Assistant.
    - name: Human‑readable display name for the Assistant.

    Usage
    - If omitted, build_agent() will construct an Assistant using these defaults.
    - You can pass a customized instance to build_agent(client, spec) to
      override any of the fields.
    - app.py also supports a --model flag that overrides spec.model at runtime.
    """
    model: str = DEFAULT_MODEL
    instructions: str = DEFAULT_INSTRUCTIONS
    name: str = "Generic AI Agent"


def build_agent(client: OpenAI, spec: Optional[AgentSpec] = None):
    """Create (or reuse) the Assistant definition via the OpenAI Assistants API.

    Parameters
    - client: an initialized OpenAI client
    - spec: optional AgentSpec to override model/instructions/name. If None
      (the default), a new ``AgentSpec()`` with default values is used. The
      annotation ``Optional[AgentSpec] = None`` means callers may pass an
      ``AgentSpec`` instance or omit it entirely.

    Returns: the created Assistant object
    """
    # Defaulting behavior: if no spec is provided, use the default AgentSpec()
    s = spec or AgentSpec()
    assistant = client.beta.assistants.create(
        name=s.name,
        model=s.model,
        instructions=s.instructions,
    )
    return assistant


def create_session(client: OpenAI, agent_id: str):
    """Create a conversation thread for the given assistant id (id not used here).

    The returned object is a Thread that can be used with `client.beta.threads`.
    """
    return client.beta.threads.create()
