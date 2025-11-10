# Minimal Makefile for running the multi‑mode OpenAI REPL with uv
# Docs: https://docs.astral.sh/uv/

# Load variables from .env if present (e.g., UV_PYTHON). Do NOT put secrets there.
-include .env
export

.PHONY: setup run run-chat run-responses run-harness smoke help

# Optional: point to a specific interpreter (recommended via .env)
# Example: UV_PYTHON="/path/to/python" make run
PY ?= $(UV_PYTHON)
RUN_P := $(if $(PY),-p $(PY),)

# Parameterized run-time options (used by the app's CLI)
# Usage examples:
#   make run                                   # assistants mode
#   make run MODEL=gpt-4o-mini                 # override model
#   make run MODE=chat SYSTEM="You are helpful" STREAM=true
#   make run MODE=responses SYSTEM="You are helpful" STREAM=true
MODE   ?= assistants
MODEL  ?=
SYSTEM ?=
STREAM ?=

CLI_ARGS := --mode $(MODE)
ifneq ($(MODEL),)
CLI_ARGS += --model $(MODEL)
endif
ifneq ($(SYSTEM),)
CLI_ARGS += --system $(SYSTEM)
endif
# Accept common truthy values for STREAM → add --stream
ifneq ($(STREAM),)
ifeq ($(filter $(STREAM),1 true yes on TRUE YES On),$(STREAM))
CLI_ARGS += --stream
endif
endif

# 1) Install deps with uv (uses requirements.txt)
setup:
	uv pip install $(RUN_P) -r requirements.txt

# 2) Run the app (parameterized via MODE/MODEL/SYSTEM/STREAM)
run: setup
	uv run $(RUN_P) python app.py $(CLI_ARGS)

# Convenience wrappers for modes
run-chat: MODE=chat
run-chat: run

run-responses: MODE=responses
run-responses: run

# Non-interactive 5-question testing harness
run-harness: setup
	uv run $(RUN_P) python -m agentkit.harness $(CLI_ARGS)

# Offline smoke test (no network calls)
smoke: setup
	uv run $(RUN_P) python smoke_test.py

# Show quick usage with parameter examples
help:
	@echo "Usage:"
	@echo "  make setup                         # install deps"
	@echo "  make run                           # Assistants mode (default)"
	@echo "  make run MODEL=gpt-4o-mini         # set model in Assistants mode"
	@echo "  make run MODE=chat SYSTEM='You are helpful' STREAM=true"
	@echo "  make run MODE=responses SYSTEM='You are helpful' STREAM=true"
	@echo "  make run-chat                      # Chat mode shortcut"
	@echo "  make run-responses                 # Responses mode shortcut"
	@echo "  make run-harness                   # Run 5-question harness (respects MODE/MODEL/SYSTEM)"
	@echo "\nNotes:"
	@echo "  - To use a specific interpreter, set UV_PYTHON in .env (see .env.example)."
	@echo "  - OPENAI_API_KEY must be set in your OS environment."