#!/usr/bin/env python3
"""Music control via termux-media-player"""

import subprocess
import sys


def run_termux_media_player(args):
    try:
        result = subprocess.run(
            ["termux-media-player"] + args,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        print(result.stdout.strip())
    except FileNotFoundError:
        print("Error: termux-media-player not found. Install with: pkg install termux-api", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: music <play|pause|next|prev|status>")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "status":
        run_termux_media_player(["info"])
    elif cmd in ("play", "pause", "next", "prev"):
        run_termux_media_player([cmd])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Usage: music <play|pause|next|prev|status>")
        sys.exit(1)


if __name__ == "__main__":
    main()
