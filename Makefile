# Use a Python interpreter path, preferrably from .env if provided
# Managed by uv (https://docs.astral.sh/uv/)
# Common tasks for this project.

# Load variables from .env if present (e.g., UV_PYTHON)
-include .env
export

.PHONY: setup sync run smoke python info shell

VENV=venv
# Prefer UV_PYTHON from .env; otherwise auto-detect .venv, else fall back to ./venv
PY?=$(UV_PYTHON)
ifeq ($(PY),)
ifneq (,$(wildcard .venv/bin/python))
PY=.venv/bin/python
else
PY=$(VENV)/bin/python
endif
endif

# Create the local venv with uv if needed and install deps using uv
setup:
ifeq ($(UV_PYTHON),)
# Only create ./venv if we're actually targeting it (not when using .venv)
ifneq (,$(findstring $(VENV)/bin/python,$(PY)))
	@if [ ! -d "$(VENV)" ]; then \
		uv venv $(VENV); \
	fi
endif
endif
	uv pip install -p $(PY) -r requirements.txt

# Re-sync the environment strictly to requirements.txt (removes extras)
sync:
	uv pip sync -p $(PY) requirements.txt

# Run the application via the selected interpreter (UV_PYTHON or local venv)
run: setup
	uv run -p $(PY) python app.py

# Run the offline smoke test via the selected interpreter
smoke: setup
	uv run -p $(PY) python smoke_test.py

# Drop into a Python REPL inside the selected interpreter env
python: setup
	uv run -p $(PY) python

# Start a subshell inside the selected environment (Unix shells).
# - If an activate script exists next to $(PY) (e.g., .venv/bin/activate or venv/bin/activate), use it.
# - Otherwise, fall back to `uv run -p $(PY) bash -l` which runs a shell in the chosen interpreter context.
shell:
	@if [ -f "$(dir $(PY))activate" ]; then \
		echo "Activating $(dir $(PY))activate and starting bash -l ..."; \
		bash -lc "source $(dir $(PY))activate && bash -l"; \
	else \
		echo "No activate script found next to $(PY). Falling back to 'uv run -p $(PY) bash -l' ..."; \
		uv run -p $(PY) bash -l; \
	fi

# Display interpreter path for IDE configuration
info:
	@echo "Interpreter path used by Make targets (from .env UV_PYTHON if set; else ./.venv or ./venv):"
	@echo "$(abspath $(PY))"

# Remove local environments (use with care)
.PHONY: clean clean-venv clean-dotvenv
clean-venv:
	@if [ -d "venv" ]; then \
		echo "Removing ./venv ..."; \
		rm -rf venv; \
		echo "./venv removed."; \
	else \
		echo "./venv does not exist (nothing to do)."; \
	fi

clean-dotvenv:
	@if [ -d ".venv" ]; then \
		echo "Removing ./.venv ..."; \
		rm -rf .venv; \
		echo "./.venv removed."; \
	else \
		echo "./.venv does not exist (nothing to do)."; \
	fi

# Convenience: remove both variants
clean: clean-venv clean-dotvenv