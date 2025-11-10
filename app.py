import argparse
import os
from typing import Optional

from openai import OpenAI

from agentkit.builder import AgentSpec, build_agent, create_session
from agentkit.repl import run_repl


def get_model_override() -> Optional[str]:
    """Parse the optional --model CLI flag and return its value.

    Purpose
    - Allows you to override the default model defined in AgentSpec at runtime
      without editing code.

    Behavior
    - Returns the model name string when provided (e.g., "gpt-4o-mini").
    - Returns None when --model is not passed, so callers can keep defaults.

    Example
    - python app.py --model gpt-4o-mini
    """
    parser = argparse.ArgumentParser(description="Generic OpenAI Agents REPL")
    parser.add_argument("--model", help="Override model name (default from AgentSpec)")
    args = parser.parse_args()
    return args.model


def main() -> int:
    """High-level entrypoint for a generic OpenAI Assistant REPL.

    What it does
    - Reads OPENAI_API_KEY from the OS environment.
    - Constructs an OpenAI SDK client (no network call on construction).
    - Builds an Assistant and creates a Thread via agentkit.builder.
    - Starts the interactive loop via agentkit.repl.run_repl.

    Inputs
    - CLI: optional --model flag parsed by get_model_override() to override AgentSpec.model.

    Environment
    - OPENAI_API_KEY: API authentication (must be set in your OS environment).

    Returns
    - int: 0 on success, 1 if assistant/thread creation fails.

    Notes
    - Prints a warning if API key is missing; the app will not be able to call the API.
    - Network requests occur only when calling the OpenAI client methods (assistant/thread creation and REPL runs).
    """
    # Read API key from environment (prefer global OS env)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY is not set. The app will not be able to call the API.")

    # OpenAI here is the Python SDK client class (from `openai` package)
    # Constructing the client does not make a network call; it automatically reads configuration
    # from environment variables (e.g., OPENAI_API_KEY) when no api_key is passed.
    client = OpenAI()

    # Build assistant and thread
    spec = AgentSpec()
    override = get_model_override()
    if override:
        spec.model = override

    try:
        assistant = build_agent(client, spec)
        thread = create_session(client, assistant.id)
    except Exception as e:
        print("ERROR: Failed to create assistant/thread:", e)
        return 1

    run_repl(
        client,
        thread,
        assistant_id=assistant.id,
        intro="🤖 Generic AI Agent — type 'exit' to quit",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
