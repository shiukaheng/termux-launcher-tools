# Termux Launcher Tools - Requirements

This document describes the dependencies, setup requirements, and environment configuration for all tools in this repository.

## System Requirements

- **Platform**: Android with Termux installed
- **Python**: 3.x (`pkg install python`)
- **Shell**: Bash

## Core Dependencies

### Termux Packages

Install via `pkg install`:

```bash
pkg install python
pkg install aapt          # For app indexing (launchindexer)
pkg install termux-api    # For termux-* commands
```

### Python Packages

Most tools use only Python standard library. Exceptions:

| Tool | Package | Install |
|------|---------|---------|
| `repllm` | `openai` | `pip install openai` |

### Custom Tools Expected

These external tools are expected to be installed separately:

| Tool | Purpose | Location |
|------|---------|----------|
| `mcp-cli` | Beeper MCP client | `~/.local/bin/mcp-cli` |
| `grun` | glibc runner (Termux) | `/data/data/com.termux/files/usr/glibc/bin/grun` |

#### mcp-cli Installation

`mcp-cli` is a compiled Bun binary for interacting with MCP servers.

**Build process for Linux ARM64 (Termux):**

1. Clone the mcp-cli repo
2. Build with Docker using Bun's cross-compile:
   ```bash
   docker build -t mcp-cli-builder -f Dockerfile.mcp-cli .
   ```
   Where `Dockerfile.mcp-cli` contains:
   ```dockerfile
   FROM oven/bun:latest
   WORKDIR /app
   COPY . .
   RUN bun install --frozen-lockfile
   RUN bun build --compile --minify --target=bun-linux-arm64 src/index.ts --outfile /output/mcp-cli-linux-arm64
   ```
3. Extract binary from Docker image
4. On Termux, create wrapper script using `grun`:
   ```bash
   mv ~/.local/bin/mcp-cli ~/.local/bin/mcp-cli-raw
   cat > ~/.local/bin/mcp-cli << 'EOF'
   #!/bin/bash
   exec grun ~/.local/bin/mcp-cli-raw "$@"
   EOF
   chmod +x ~/.local/bin/mcp-cli
   ```

**Config file**: `~/.config/mcp/mcp_servers.json`

## Environment Variables

### repllm

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | OpenAI API key | - | Yes |
| `API_ENDPOINT` | API endpoint URL | `https://api.openai.com/v1` | No |
| `MODEL` | Model to use | `gpt-4o` | No |
| `PREPROMPT_FILE` | Path to preprompt file | - | No |
| `CONTEXT_MD_DIR` | Directory of .md files to load into context | - | No |

#### CONTEXT_MD_DIR

Set to a directory path containing `.md` files. All markdown files are loaded alphabetically and appended to the system prompt.

```bash
export CONTEXT_MD_DIR="$HOME/agent_skills"
```

Use this to provide the LLM with:
- API documentation
- Skill definitions
- Reference guides
- Custom instructions

### Preprompt File

The preprompt file defines the system prompt and available commands. See `preprompt` in the repo root for an example.

## Tool-Specific Requirements

### launch / launchindexer

- Requires `aapt` for app indexing
- Creates app cache at `~/.termux-launcher/apps.json`
- Run `launchindexer --reindex` after installation

### notifications

- Requires modified `termux-api` APK with:
  - `NotificationCancel` API
  - `NotificationAction` API
- See sibling repo `termux-api` for modified APK

### compass

- Uses `urllib` for geocoding (no external deps)
- Requires compass app installed (launches via intent)

### music / volume

- Uses Android `cmd media_session` command
- No additional dependencies

### status

- Uses Termux built-in commands
- No additional dependencies

## Directory Structure

```
~/repos/termux-launcher-tools/
├── launch
├── launchindexer
├── music
├── notifications
├── notifywatch
├── preprompt
├── repllm
├── status
├── update
├── volume
├── compass
├── compass-raw
├── lib/
│   ├── __init__.py
│   ├── apps.py
│   └── fuzzy.py
├── AGENTS.md
├── README.md
└── requirements.md    (this file)

~/.termux-launcher/
└── apps.json          # Cached app index

~/.config/mcp/
└── mcp_servers.json   # MCP server config

~/.local/bin/
├── mcp-cli            # MCP CLI wrapper
└── mcp-cli-raw        # Actual binary

~/agent_skills/        # CONTEXT_MD_DIR (optional)
├── beeper.md
└── daily_report.md
```

## Bashrc Setup

Add to `~/.bashrc`:

```bash
export PATH="$HOME/repos/termux-launcher-tools:$PATH"

# Aliases
alias l="launch"
alias li="launchindexer"
alias n="notifications"
alias m="music"
alias s="status"
alias u="update"
alias x="exit"
alias c="clear"

# repllm env vars
export API_KEY="your-api-key"
export API_ENDPOINT="https://api.openai.com/v1"
export MODEL="gpt-4o"
export PREPROMPT_FILE="$HOME/repos/termux-launcher-tools/preprompt"
export CONTEXT_MD_DIR="$HOME/agent_skills"
alias a="repllm"
```

## Extending

### Adding a New Tool

1. Create executable Python script in repo root
2. Use `#!/usr/bin/env python3` shebang
3. Import from `lib/` if needed (fuzzy search, app index)
4. Keep dependencies minimal - prefer stdlib
5. Update `AGENTS.md` with tool documentation
6. Add to preprompt if LLM should use it

### Adding Context Files

1. Create `.md` file in `CONTEXT_MD_DIR`
2. Files are loaded alphabetically
3. Use for API docs, skill definitions, reference material
4. Keep concise - loaded into every session

### Modifying Preprompt

Edit `preprompt` file to:
- Add new commands
- Change LLM behavior
- Add domain-specific instructions
- Define new workflows

## Troubleshooting

### "command not found"

Ensure PATH includes the repo:
```bash
export PATH="$HOME/repos/termux-launcher-tools:$PATH"
```

### mcp-cli fails with "cannot execute"

On Termux, ensure wrapper script uses `grun`:
```bash
cat ~/.local/bin/mcp-cli
# Should show: exec grun ~/.local/bin/mcp-cli-raw "$@"
```

### notifications tap/reply does nothing

- Ensure screen is ON
- Check modified termux-api APK is installed
- Some apps don't support notification actions

### launchindexer returns no apps

Run with `--reindex`:
```bash
launchindexer --reindex
```
