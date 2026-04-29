# Termux Launcher Tools

A collection of lightweight command-line tools for Termux on Android.

## Tools

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `launch` | Fuzzy app launcher | stdlib only |
| `launchindexer` | Index installed apps | stdlib only |
| `music` | Media control (play/pause/next/prev/volume) | stdlib only |
| `status` | System status display (battery, network, etc.) | stdlib only |
| `compass` | Launch compass with location geocoding | stdlib only |
| `notifications` | Notification manager | stdlib only |
| `update` | Update this repo from GitHub | stdlib only |
| `repllm` | REPL for OpenAI-compatible models with tool support | `openai` |

## Requirements

### All Tools
- Python 3 (comes with Termux)
- Termux:API app (for some tools that use `termux-api`)

### repllm Only
```bash
pip install openai
```

Additionally, set these environment variables (add to `~/.bashrc`):
```bash
export API_KEY="your-api-key-here"
export API_ENDPOINT="https://openrouter.ai/api/v1"  # or your preferred endpoint
export MODEL="moonshotai/kimi-k2.5"  # or your preferred model
```

Optional:
```bash
export PREPROMPT_FILE="/path/to/system_prompt.txt"
```

## Installation

```bash
cd ~
git clone https://github.com/shiukaheng/termux-launcher-tools.git
cd termux-launcher-tools

# Make all tools executable (if not already)
chmod +x launch launchindexer music status compass notifications update repllm

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/termux-launcher-tools:$PATH"
```

## Design Philosophy

- **Lightweight**: No package managers like `uv` or virtual environments
- **Minimal dependencies**: Only `openai` for `repllm`, everything else uses Python stdlib
- **Self-contained**: Each tool is a single Python file
- **Termux-first**: Designed for Android/Termux environment

## Tool Details

### `launch` - Fuzzy App Launcher
```bash
launch whatsapp      # Fuzzy search and launch
launch --reindex     # Rebuild app index
launch --list        # List all indexed apps
```

### `music` - Media Control
```bash
music play           # Play
music pause          # Pause
music toggle         # Play/Pause toggle
music next           # Next track
music prev           # Previous track
music volume         # Get current volume
```

### `status` - System Status
```bash
status               # Show battery, network, storage info
```

### `compass` - Compass Launcher
```bash
compass              # Launch compass app
compass "New York"   # Launch compass with geocoded location
```

### `repllm` - LLM REPL
```bash
repllm               # Start interactive REPL
```

Commands inside REPL:
- `.help` - Show available commands
- `.tokens` - Show token usage for this session
- `.exit` or `.quit` - Exit REPL

The `bash` tool allows running shell commands. Ctrl-C cancels the current operation.

### `update` - Update Tools
```bash
update               # git pull from this repo
```
