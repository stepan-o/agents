"""AgentKit package

Building blocks for constructing and running generic OpenAI assistants and
other experimentation modes (Chat Completions, Responses API).

Modules:
- builder: utilities to construct the assistant and create a thread using the OpenAI SDK (Assistants)
- repl: simple REPL loop utilities for running interactive sessions (Assistants)
- chat_completions: REPL using Chat Completions API
- responses_mode: REPL using Responses API

Re-exports:
- AgentSpec, build_agent, create_session, run_repl, chat_loop, responses_loop for convenience imports.
"""

from .builder import AgentSpec, build_agent, create_session
from .repl import run_repl
from .chat_completions import chat_loop
from .responses_mode import responses_loop

__all__ = [
    "AgentSpec",
    "build_agent",
    "create_session",
    "run_repl",
    "chat_loop",
    "responses_loop",
]
