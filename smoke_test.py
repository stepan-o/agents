"""
A minimal smoke test that verifies local environment and imports.
This script does NOT make any network/API calls.
"""
import os
import sys


def main() -> int:
    print("[1/4] Checking Python version...")
    print(f"Python: {sys.version.split()[0]}")

    print("[2/4] Checking environment variables...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OPENAI_API_KEY: found (length hidden)")
    else:
        print("WARNING: OPENAI_API_KEY not set. The app will not be able to call the API.")

    print("[3/4] Verifying OpenAI SDK import and basic client construction...")
    try:
        from openai import OpenAI  # type: ignore
        _client = OpenAI()  # uses env var if present; does not make a request
        print("OpenAI client constructed successfully (no network call made).")
    except Exception as e:
        print("ERROR: Failed to import or construct OpenAI client:")
        print(e)
        return 1

    print("[4/4] Verifying local agents package imports...")
    try:
        from agents.builder import AgentSpec, build_agent, create_session  # type: ignore
        from agents.repl import run_repl  # type: ignore
        _ = (AgentSpec, build_agent, create_session, run_repl)
        print("agents package imported successfully.")
    except Exception as e:
        print("ERROR: Failed to import local agents package:")
        print(e)
        return 1

    print("\nSmoke test passed. Your environment looks good.")
    print("Next: `python app.py` to run the REPL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
