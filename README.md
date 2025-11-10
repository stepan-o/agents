# openai-agents-starter

A minimal Python REPL app using the OpenAI Python SDK (Assistants/Threads/Runs). It provides a generic framework to define, connect to, and test OpenAI assistants (agents) using different APIs. Runtime logic is organized in the local `agentkit/` package for clarity and extensibility.

## Quick start
- Option A — Use an existing uv environment via `.env` (preferred):
  1) Copy example env and set interpreter path
     ```bash
     cp .env.example .env
     # Set UV_PYTHON to your env's python path. Discover with:
     uv run -n agents python -c "import sys; print(sys.executable)"
     ```
  2) Install deps and run
     ```bash
     make setup
     make run
     ```
- Option B — Use a local uv‑managed venv automatically:
  ```bash
  make setup   # creates ./venv if missing and installs dependencies
  make run     # runs the app using the selected interpreter
  ```

Other helpful commands
```bash
make smoke   # run offline smoke test
make python  # open a Python REPL inside the selected interpreter env
make shell   # start a subshell in the selected env (.venv/venv activate if available; else uv-run fallback)
make info    # print the interpreter path that will be used
```

## Run the app
Using Makefile (recommended):
```bash
make run
```
Manual (local venv case):
```bash
source venv/bin/activate   # macOS/Linux
# .\venv\Scripts\activate  # Windows PowerShell
python app.py
```
The console starts a simple REPL. Type your messages; type `exit` to quit.

## Environment
- OPENAI_API_KEY — your OpenAI API key (must be set in your OS environment; do not put secrets in .env).
- UV_PYTHON (optional, preferred) — full path to the Python interpreter of a uv‑created environment. When set in `.env`, all Make targets use it instead of `./venv/bin/python`.

Set OPENAI_API_KEY globally (examples):
- macOS/Linux (current shell session):
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```
- macOS/Linux (persist for your user, e.g., bash): add to ~/.bashrc or ~/.zshrc:
  ```bash
  echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc && source ~/.zshrc
  ```
- Windows PowerShell (current session):
  ```powershell
  $Env:OPENAI_API_KEY = "sk-..."
  ```
- Windows (persist):
  ```powershell
  setx OPENAI_API_KEY "sk-..."
  ```

Optional: copy .env.example to .env only to set UV_PYTHON (interpreter path), not secrets.
```bash
cp .env.example .env
# edit .env to set UV_PYTHON if you want Makefile to use a specific interpreter
```

## Smoke test (offline)
```bash
make smoke
# or manually (local venv)
source venv/bin/activate && python smoke_test.py
```

## IDE setup (concise)
- Print the exact interpreter path your Make targets use:
  ```bash
  make info
  ```
- PyCharm → Settings/Preferences → Project → Python Interpreter → Add → Existing → choose the path shown by `make info`.
- Common paths for reference:
  - .venv (uv‑managed, project local): `<project_root>/.venv/bin/python` (macOS/Linux) or `<project_root>\.venv\Scripts\python.exe` (Windows)
  - venv (fallback created by `make setup`): `<project_root>/venv/bin/python` or `<project_root>\venv\Scripts\python.exe`

## Architecture (short)
- app.py — entrypoint. Builds the OpenAI client, constructs assistant/thread via `agentkit.builder`, runs the REPL from `agentkit.repl`. Supports `--model` override.
- agentkit/
  - builder.py — builds the Assistant (Assistants API) and creates a Thread. Central place to change model/instructions/name.
  - repl.py — minimal REPL loop to send user messages and print replies.
  - __init__.py — re‑exports common symbols for convenient imports.

---

# Extras

## Troubleshooting
- uv says “No interpreter found”
  - Ensure `UV_PYTHON` points to a real python (discover with `uv run -n <env> python -c "import sys; print(sys.executable)"`).
  - Or create the local venv: `make setup` (run from the project root).
- pip installs into the wrong Python
  - Use `make setup`, or run: `$(make info | tail -1) -m pip install -r requirements.txt`.
- PyCharm uses a different interpreter
  - Point the IDE to the path from `make info`.
- OpenAI SDK works in terminal but fails in IDE
  - Ensure IDE interpreter matches `make info`, then reinstall deps and reindex (PyCharm: Invalidate Caches / Restart).
- ModuleNotFoundError
  - Install deps: `make setup`.

Quick verification
```bash
make smoke
make run
```

## Deleting an old environment
- Make targets (safe):
  - Delete ./venv: `make clean-venv`
  - Delete ./.venv: `make clean-dotvenv`
  - Delete both: `make clean`
- Manual
  - macOS/Linux: `rm -rf venv` and/or `rm -rf .venv`
  - Windows PowerShell: `Remove-Item -Recurse -Force venv` and/or `Remove-Item -Recurse -Force .venv`
After deleting: switch IDE interpreter if needed (see `make info`), then `make setup`, then verify with `make smoke` and `make run`.

## Using uv add (optional)
With root `pyproject.toml`, you can manage deps via uv:
```bash
uv add openai python-dotenv
```
If you see “No `pyproject.toml` found…”, run commands from the project root. You can still use requirements.txt via `make setup`. Both approaches work with the interpreter from `make info`.

## Connect this project to GitHub (optional)
Terminal:
```bash
git init && git checkout -b main
git remote add origin https://github.com/<you>/<repo>.git
git add -A && git commit -m "Initial commit" && git push -u origin main
```
- Use a Personal Access Token for HTTPS or set up SSH keys.
PyCharm:
- VCS → Enable Version Control Integration → Git
- VCS → Import into Version Control → Share Project on GitHub… (or add remote in VCS → Git → Remotes… and Push)



## Connect this project to GitHub

Follow either the Terminal (outside IDE) path or the PyCharm (inside IDE) path. Both end with the code pushed to a GitHub repository.

Important safety note: Secrets like `.env` are already gitignored in this repo. Do not commit real API keys.

### Option A — Terminal (outside the IDE)

1) Prerequisites
- Install Git: macOS (brew install git) • Ubuntu/Debian (sudo apt-get install git) • Windows (install Git for Windows).
- Create or sign into your GitHub account.
- Configure Git identity (once per machine):
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```

2) Initialize local repo (if not already a Git repo)
```bash
cd <project_root>
git init
# Optional: set default branch name to main (if your Git defaults to master)
git checkout -b main
```

3) Verify .gitignore protects secrets and venvs
- This repo includes a .gitignore that ignores `.env`, `.venv/`, and `venv/`. No action needed unless you customized it.

4) Create a repo on GitHub
- Go to https://github.com/new
- Repository name: openai-agents-starter (or your preferred name)
- Visibility: Public or Private
- Do NOT initialize with a README/.gitignore/license (we already have them locally)
- Click “Create repository” and copy the commands GitHub shows for pushing an existing repo.

5) Add the remote and push
- Using HTTPS (simpler to start):
  ```bash
  git remote add origin https://github.com/<your-username>/<your-repo>.git
  git add -A
  git commit -m "Initial commit: scaffolded agents-based REPL"
  git push -u origin main
  ```
- Using SSH (recommended once keys are set up):
  - Create a new SSH key if you don’t have one and add to GitHub:
    ```bash
    ssh-keygen -t ed25519 -C "you@example.com"
    # Press Enter to accept defaults; add a passphrase if you like
    eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519
    pbcopy < ~/.ssh/id_ed25519.pub   # macOS; on Linux: xclip -sel clip < ~/.ssh/id_ed25519.pub
    ```
    Then paste the copied key at https://github.com/settings/keys → New SSH key.
  - Add SSH remote and push:
    ```bash
    git remote remove origin  # if you added HTTPS first (optional)
    git remote add origin git@github.com:<your-username>/<your-repo>.git
    git push -u origin main
    ```

6) Authentication tips
- HTTPS: GitHub recommends using a Personal Access Token (PAT) instead of a password. Create one at https://github.com/settings/tokens and use it when prompted.
- SSH: After adding your key, test it with `ssh -T git@github.com`.

7) Common terminal troubleshooting
- Remote already exists:
  ```bash
  git remote set-url origin https://github.com/<your-username>/<your-repo>.git
  ```
- Default branch mismatch (master vs main):
  ```bash
  git branch -M main
  git push -u origin main
  ```
- Large files rejected: consider Git LFS — https://git-lfs.com/

### Option B — PyCharm (inside the IDE)

1) Enable Git for the project (if not already)
- PyCharm → VCS menu → Enable Version Control Integration → choose “Git”.
- If a Git repo exists, PyCharm will detect it automatically.

2) Initial commit
- VCS → Commit (or use the Commit tool window).
- Review changed files; ensure `.env` is listed under Ignored (should be, due to .gitignore).
- Write a message like “Initial commit: scaffolded agents-based REPL” and click Commit (or Commit and Push).

3) Share project on GitHub (creates the remote)
- VCS → Import into Version Control → Share Project on GitHub…
- Log into GitHub in the dialog if prompted.
- Set Repository name (e.g., openai-agents-starter) and visibility.
- Click Share. PyCharm creates a repo on GitHub and pushes your current branch.

Alternative if “Share…” is not shown:
- VCS → Git → Remotes… → add origin with either HTTPS or SSH URL from GitHub.
- Then VCS → Git → Push…

4) Verify
- After pushing, PyCharm shows a link to the repository. Click it to open the GitHub page.

5) IDE troubleshooting
- “.env still shows up to commit”: Check that .env is listed in .gitignore. If not, add `.env` and re-run Commit tool window → Refresh. This repo already includes it.
- “Auth failed” on push:
  - HTTPS: Use a GitHub token (PyCharm will offer to create one).
  - SSH: Ensure your SSH key is added to the ssh-agent and to your GitHub account.

### Next steps (optional but recommended)
- Add a repository description, topics, and a README badge.
- Protect the main branch (GitHub → Settings → Branches → Add rule; require PRs and reviews).
- Set up GitHub Actions (CI) later if desired.
- Add collaborators in GitHub → Settings → Collaborators.








## Rename the project folder (optional)

To rename the folder on disk and keep everything working:

1) Close the project in your IDE (PyCharm) to release file handles.
2) In a terminal, rename the directory:
   - macOS/Linux:
     ```bash
     cd ..
     mv PythonProject openai-agents-starter
     ```
   - Windows PowerShell:
     ```powershell
     Rename-Item -Path .\PythonProject -NewName openai-agents-starter
     ```
3) Reopen the project from its new location in PyCharm.
4) Interpreter check:
   - This repo’s Makefile and .env are resilient to folder renames. `.env` now sets
     `UV_PYTHON="${PWD}/.venv/bin/python"`, so paths auto-adjust to the current folder.
   - Verify with:
     ```bash
     make info
     ```
     If you previously pointed PyCharm to an absolute interpreter path inside the old folder,
     update it to the interpreter shown by `make info`.
5) Verify everything:
   ```bash
   make smoke
   make run
   ```



## Use the existing uv .venv in your IDE (no new env)
If this project already has a uv-managed virtual environment in the project folder named `.venv`, you can point your IDE to it so you don’t create a new environment.

Quick check: print the interpreter path that project tools will use
- Run: `make info`
- You should see something like `<project>/.venv/bin/python` (macOS/Linux) or `<project>\.venv\Scripts\python.exe` (Windows).

PyCharm
1) Open Settings/Preferences → Project: openai-agents-starter → Python Interpreter.
2) Click the gear icon → Add Interpreter… → Add Local Interpreter → Existing.
3) Interpreter path:
   - macOS/Linux: <project>/.venv/bin/python
   - Windows: <project>\.venv\Scripts\python.exe
4) Make sure you are selecting "Existing" and not creating a new virtualenv. Leave "Inherit global site-packages" unchecked.
5) Apply/OK. PyCharm will index packages from this environment. No new env will be created.

VS Code
- Command Palette → "Python: Select Interpreter" → pick the one that points to <project>/.venv (it will usually display the path).
- If it doesn’t appear, choose "Enter interpreter path" and browse to:
  - macOS/Linux: <project>/.venv/bin/python
  - Windows: <project>\.venv\Scripts\python.exe
- Optional: set it persistently in `.vscode/settings.json`:
  - `{ "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python" }` (adjust for Windows path if needed).

Notes
- You do not need to recreate the environment if `.venv` already exists and contains your modules.
- All Make targets already prefer `.venv` automatically. If you want to force a different interpreter, set `UV_PYTHON` in `.env` (see .env.example) and `make info` to confirm.
- If your IDE auto-creates environments, disable that option or always choose "Existing" when prompted.


## FAQ: What do I enter for "Path to uv" in the IDE?
When your IDE asks for the "Path to uv", it needs the path to the uv executable (the Astral package/dependency manager) — not the Python interpreter inside your virtual environment.

How to find the uv executable on your system
- macOS/Linux (bash/zsh):
  - `command -v uv` or `which uv`
- Windows PowerShell:
  - `Get-Command uv | Select -Expand Source`
- Windows cmd:
  - `where uv`

Typical locations (for reference)
- macOS Apple Silicon (Homebrew): `/opt/homebrew/bin/uv`
- macOS Intel (Homebrew): `/usr/local/bin/uv`
- macOS/Linux (official installer or pipx): `~/.local/bin/uv`
- Windows (official installer or pipx): `%USERPROFILE%\.local\bin\uv.exe`
- Windows (Scoop): `C:\Users\<you>\scoop\shims\uv.exe`
- Windows (Chocolatey): `C:\ProgramData\chocolatey\bin\uv.exe`

Notes
- Point the IDE to the uv executable above. Separately, when selecting a Python interpreter for this project, choose the existing `.venv` interpreter (e.g., `<project>/.venv/bin/python` or `<project>\.venv\Scripts\python.exe`).
- You generally do not install uv inside a venv; it is a standalone tool on your PATH.
