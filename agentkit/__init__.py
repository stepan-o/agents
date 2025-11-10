"""AgentKit package

Building blocks for constructing and running generic OpenAI assistants.

Modules:
- builder: utilities to construct the assistant and create a thread using the OpenAI SDK
- repl: simple REPL loop utilities for running interactive sessions

Re-exports:
- AgentSpec, build_agent, create_session, run_repl for convenience imports.
"""

from .builder import AgentSpec, build_agent, create_session
from .repl import run_repl

__all__ = [
    "AgentSpec",
    "build_agent",
    "create_session",
    "run_repl",
]
