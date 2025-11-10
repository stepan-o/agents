"""Application entrypoint for experimenting with OpenAI in multiple modes.

This module wires a small CLI to three runtime paths implemented in `agentkit/`:
- assistants: Uses the Assistants/Threads/Runs APIs (server-side thread state)
- chat: Uses the Chat Completions API (client-side transcript)
- responses: Uses the Responses API (client-side transcript)

It constructs a single `OpenAI` client (reading `OPENAI_API_KEY` from your OS
environment) and routes control based on `--mode`. This file intentionally keeps
policy/behavior minimal; see individual modules in `agentkit/` for details.

Quick start:
- `make run`                 → Assistants mode (default)
- `make run-chat`            → Chat Completions mode
- `make run-responses`       → Responses API mode
- `python app.py --help`     → Show all options
"""

import argparse
import os

from openai import OpenAI

from agentkit.builder import AgentSpec, build_agent, create_session
from agentkit.repl import run_repl
from agentkit import chat_loop, responses_loop


def parse_args():
    """Define and parse CLI flags for selecting mode and behavior.

    Flags
    - --mode {assistants,chat,responses}: Selects which API the REPL uses. Defaults to assistants.
    - --model <name>: Overrides the model used by the selected mode (Assistants uses AgentSpec.model).
    - --system <text>: Sets a system prompt/instructions for chat/responses modes.
    - --stream: Enables best-effort streaming for chat/responses modes (ignored in assistants mode).
    """
    parser = argparse.ArgumentParser(description="Generic OpenAI Agents/Chat/Responses REPL")

    # Model override applies to all modes. For Assistants, it updates AgentSpec.model.
    parser.add_argument("--model", help="Override model name (default from AgentSpec or mode default)")

    # Mode determines which submodule runs (assistants/chat/responses).
    parser.add_argument(
        "--mode",
        choices=["assistants", "chat", "responses"],
        default="assistants",
        help="Interaction mode: assistants (default), chat (Chat Completions), responses (Responses API)",
    )

    # Streaming flag is only meaningful for chat/responses; Assistants REPL is non-streaming.
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming output when supported (chat/responses modes)",
    )

    # System prompt is used to seed local transcripts in chat/responses modes.
    parser.add_argument(
        "--system",
        help="Override system prompt/instructions for chat/responses modes",
    )
    return parser.parse_args()


def main() -> int:
    """High-level entrypoint for generic OpenAI experimentation modes.

    Modes
    - assistants: Assistants/Threads/Runs via agentkit.builder + agentkit.repl
    - chat: Chat Completions API via agentkit.chat_completions.chat_loop
    - responses: Responses API via agentkit.responses_mode.responses_loop
    """
    args = parse_args()

    # Read API key from environment (prefer global OS env). The OpenAI SDK
    # automatically reads `OPENAI_API_KEY` when constructing the client below.
    # We warn early if it's missing so the user sees a friendly message.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY is not set. The app will not be able to call the API.")

    # Construct a single client instance shared across modes. Creating the
    # client does not perform a network call; API requests happen on method use.
    client = OpenAI()

    # Assistants mode: create (or reuse) an Assistant and a Thread, then run the
    # Assistants REPL. `--model` overrides the spec's model at runtime.
    if args.mode == "assistants":
        spec = AgentSpec()
        if args.model:
            spec.model = args.model  # Example to override instructions for Assistants:
                                     # spec.instructions = "You are ..."  # prefer using AgentSpec
        try:
            assistant = build_agent(client, spec)
            thread = create_session(client, assistant.id)
        except Exception as e:
            print("ERROR: Failed to create assistant/thread:", e)
            return 1
        # Use default intro/prompt from run_repl(); do not override by default.
        # To customize the intro, pass intro=... to run_repl().
        run_repl(
            client,
            thread,
            assistant_id=assistant.id,
        )
        return 0

    # Chat Completions mode: maintain a local transcript and call the Chat API
    # each turn. `--system` seeds the transcript; `--stream` enables best-effort
    # token streaming when supported by the SDK/model.
    if args.mode == "chat":
        # Use defaults from chat_completions.chat_loop unless overrides are provided.
        # Example to override in code (prefer CLI flags):
        # chat_loop(client, model="gpt-4o-mini", system_prompt="You are helpful", intro="...", stream=True)
        kwargs = {}
        if args.model:
            kwargs["model"] = args.model
        if args.system:
            kwargs["system_prompt"] = args.system
        if args.stream:
            kwargs["stream"] = True
        chat_loop(client, **kwargs)
        return 0

    # Responses API mode: similar console UX but uses the Responses endpoint
    # under the hood instead of Chat Completions.
    if args.mode == "responses":
        # Use defaults from responses_mode.responses_loop unless overrides are provided.
        # Example to override in code (prefer CLI flags):
        # responses_loop(client, model="gpt-4o-mini", system_prompt="You are helpful", intro="...", stream=True)
        kwargs = {}
        if args.model:
            kwargs["model"] = args.model
        if args.system:
            kwargs["system_prompt"] = args.system
        if args.stream:
            kwargs["stream"] = True
        responses_loop(client, **kwargs)
        return 0

    # Defensive guard: argparse should restrict values, but keep a fallback.
    print(f"Unknown mode: {args.mode}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
