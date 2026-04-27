# Termux Launcher Tools

A suite of CLI tools that make Termux a daily launcher for Android apps. Pure Python with no external dependencies.

## Overview

This repo provides command-line tools for controlling an Android phone via Termux. It works alongside a modified `termux-api` app (see sibling repo `termux-api`) that exposes additional Android APIs.

## Tools

| Command | Alias | Description |
|---------|-------|-------------|
| `launch` | `l` | Fuzzy app launcher |
| `launchindexer` | - | App indexing and discovery |
| `music` | `m` | System media control (play/pause/next/prev) |
| `notifications` | `n` | Notification manager (list/cancel/action) |
| `status` | `s` | System status (battery/network/storage/memory/uptime) |
| `compass` | - | Launch compass with optional geocoded waypoint |
| `update` | `u` | Pull latest from GitHub |

## Architecture

```
termux-launcher-tools/
├── launch          # Fuzzy app launcher
├── launchindexer   # App indexing and discovery
├── music           # Media control via cmd media_session
├── notifications   # Notification manager via termux-api
├── status          # System status display
├── compass         # Compass with geocoding
├── update          # Self-updater
└── lib/
    ├── __init__.py
    ├── apps.py     # App indexing and search logic
    └── fuzzy.py    # Levenshtein distance implementation
```

## Data Storage

- `~/.termux-launcher/apps.json` - Cached app index with package names, labels, and launch activities

## Dependencies

### On Device
- Python 3 (via `pkg install python`)
- `aapt` (via `pkg install aapt`) - for app indexing
- `termux-api` package (via `pkg install termux-api`) - CLI scripts

### Modified termux-api App
The sibling `termux-api` repo has modifications to expose:
- `NotificationCancel` - Cancel notifications by key, pkg/tag/id, or all
- `NotificationAction` - Fire notification contentIntent (action 0) or action buttons (1+)

Build and install the modified APK from `termux-api/app/build/outputs/apk/debug/`.

## Usage Examples

```
# App launching
launch chrome              # Launch Chrome
launch chatgpt             # Launch ChatGPT (fuzzy match)
launch google -a 2         # Launch Google with activity #2
launch google -a SearchActivity  # Launch by activity name

# App discovery
launchindexer              # List all apps
launchindexer googl        # List apps matching "googl"
launchindexer --activities google  # List activities for Google
launchindexer --reindex    # Rebuild app index

# Media control
music toggle               # Play/pause toggle
music next                 # Next track
music volume               # Show volume

# Notifications
notifications list         # List all notifications
notifications list -v      # Verbose (show actions/keys)
notifications action 0 0   # Tap notification [0]
notifications cancel --all # Clear all notifications

# System
status                     # Show system status

# Compass
compass                    # Launch compass (north mode)
compass london             # Navigate to London
compass "New York"         # Navigate to New York

# Self-update
update                     # Pull latest from GitHub
```

## Setup

1. Clone repo to `~/repos/termux-launcher-tools`
2. Add to `~/.bashrc`:
   ```
   export PATH="$HOME/repos/termux-launcher-tools:$PATH"
   alias l="launch"
   alias li="launchindexer"
   alias n="notifications"
   alias m="music"
   alias s="status"
   alias u="update"
   alias x="exit"
   alias c="clear"
   ```
3. Run `launchindexer --reindex` to build app index
4. Install modified termux-api APK for notification features

## Related Repos

- `termux-api` (sibling) - Modified to add NotificationCancel and NotificationAction APIs
- `termux-app` - Main Termux terminal emulator
