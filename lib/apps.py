import json
import os
import subprocess
from pathlib import Path


def get_app_index_path() -> Path:
    home = os.environ.get("HOME", os.path.expanduser("~"))
    data_dir = Path(home) / ".termux-launcher"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "apps.json"


def get_all_packages() -> list:
    try:
        result = subprocess.run(
            ["pm", "list", "packages", "--user", "0"],
            capture_output=True,
            text=True
        )
        packages = []
        for line in result.stdout.strip().split("\n"):
            if line.startswith("package:"):
                packages.append(line[8:])
        return packages
    except FileNotFoundError:
        return []


def get_app_label(pkg: str) -> str:
    try:
        path_result = subprocess.run(
            ["pm", "path", pkg],
            capture_output=True,
            text=True
        )
        if not path_result.stdout.strip():
            return pkg
        
        apk_path = None
        for line in path_result.stdout.strip().split("\n"):
            if line.startswith("package:"):
                apk_path = line.split(":", 1)[1]
                break
        
        if not apk_path:
            return pkg
        
        label_result = subprocess.run(
            ["aapt", "dump", "badging", apk_path],
            capture_output=True,
            text=True
        )
        
        for line in label_result.stdout.split("\n"):
            if line.startswith("application-label:"):
                label = line.split(":", 1)[1].strip().strip("'")
                return label
        
        return pkg
    except Exception:
        return pkg


def index_apps() -> dict:
    packages = get_all_packages()
    apps = []
    
    total = len(packages)
    for i, pkg in enumerate(packages):
        label = get_app_label(pkg)
        apps.append({"pkg": pkg, "label": label})
        if (i + 1) % 10 == 0 or i + 1 == total:
            print(f"Indexing: {i + 1}/{total}", end="\r")
    
    print()
    
    index_data = {
        "version": 1,
        "indexed_at": int(__import__("time").time()),
        "apps": apps
    }
    
    index_path = get_app_index_path()
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)
    
    return index_data


def load_index() -> dict | None:
    index_path = get_app_index_path()
    if not index_path.exists():
        return None
    try:
        with open(index_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def search_apps(query: str, index: dict) -> list:
    from .fuzzy import fuzzy_search
    
    apps = index.get("apps", [])
    labels = [app["label"] for app in apps]
    
    matches = fuzzy_search(query, labels, threshold_ratio=0.3)
    
    results = []
    for label, distance, ratio in matches[:5]:
        for app in apps:
            if app["label"] == label:
                results.append({**app, "distance": distance, "ratio": ratio})
                break
    
    return results


def launch_app(pkg: str) -> bool:
    try:
        subprocess.run(
            ["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"],
            capture_output=True,
            text=True
        )
        return True
    except Exception:
        return False


def list_apps(index: dict, filter_str: str = None) -> list:
    apps = index.get("apps", [])
    if filter_str:
        filter_lower = filter_str.lower()
        apps = [a for a in apps if filter_lower in a["label"].lower() or filter_lower in a["pkg"].lower()]
    return sorted(apps, key=lambda x: x["label"].lower())
