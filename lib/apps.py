import json
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def get_app_index_path() -> Path:
    home = os.environ.get("HOME", os.path.expanduser("~"))
    data_dir = Path(home) / ".termux-launcher"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "apps.json"


def get_all_packages(debug: bool = False) -> list:
    cmd = ["cmd", "package", "list", "packages"]
    if debug:
        print(f"[DEBUG] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if debug:
            print(f"[DEBUG] Return code: {result.returncode}")
            print(f"[DEBUG] stdout length: {len(result.stdout)}")
            print(f"[DEBUG] stderr: {result.stderr[:200] if result.stderr else '(empty)'}")
        packages = []
        for line in result.stdout.strip().split("\n"):
            if line.startswith("package:"):
                packages.append(line[8:])
        if debug:
            print(f"[DEBUG] Found {len(packages)} packages")
        return packages
    except FileNotFoundError as e:
        if debug:
            print(f"[DEBUG] FileNotFoundError: {e}")
        return []


def get_app_info(pkg: str) -> tuple:
    try:
        path_result = subprocess.run(
            ["cmd", "package", "path", pkg],
            capture_output=True,
            text=True
        )
        if not path_result.stdout.strip():
            return pkg, None
        
        apk_path = None
        for line in path_result.stdout.strip().split("\n"):
            if line.startswith("package:"):
                apk_path = line.split(":", 1)[1]
                break
        
        if not apk_path:
            return pkg, None
        
        label_result = subprocess.run(
            ["aapt", "dump", "badging", apk_path],
            capture_output=True,
            text=True
        )
        
        label = pkg
        activity = None
        
        for line in label_result.stdout.split("\n"):
            if line.startswith("application-label:"):
                label = line.split(":", 1)[1].strip().strip("'")
            elif line.startswith("launchable-activity:"):
                parts = line.split("'")
                for i, part in enumerate(parts):
                    if "name=" in part:
                        activity = part.split("name=")[1].strip()
                        break
                if not activity and "name='" in line:
                    activity = line.split("name='")[1].split("'")[0]
        
        return label, activity
    except Exception:
        return pkg, None


def index_apps(debug: bool = False, workers: int = 16) -> dict:
    packages = get_all_packages(debug=debug)
    apps = []
    
    total = len(packages)
    if debug:
        print(f"[DEBUG] Total packages to index: {total}")
        print(f"[DEBUG] Using {workers} worker threads")
        if total == 0:
            print("[DEBUG] No packages found! Check if 'cmd' is accessible.")
            print(f"[DEBUG] PATH: {os.environ.get('PATH', '(not set)')}")
            import shutil
            cmd_path = shutil.which("cmd")
            print(f"[DEBUG] cmd location: {cmd_path}")
    
    counter = [0]
    counter_lock = threading.Lock()
    
    def process_package(pkg):
        label, activity = get_app_info(pkg)
        with counter_lock:
            counter[0] += 1
            if counter[0] % 10 == 0 or counter[0] == total:
                print(f"Indexing: {counter[0]}/{total}", end="\r")
        return {"pkg": pkg, "label": label, "activity": activity}
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_package, pkg) for pkg in packages]
        for future in as_completed(futures):
            apps.append(future.result())
    
    print()
    
    index_data = {
        "version": 2,
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


def launch_app(pkg: str, activity: str = None) -> bool:
    def run_cmd(args):
        result = subprocess.run(args, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if "Error:" in output or "Error type" in output:
            return False, output
        return True, output
    
    try:
        if activity:
            success, output = run_cmd(["am", "start", "-n", f"{pkg}/{activity}"])
            if success:
                return True
            if "does not exist" in output or "not found" in output:
                success, _ = run_cmd(["am", "start", "-a", "android.intent.action.SEARCH", pkg])
                if success:
                    return True
        else:
            success, _ = run_cmd(["am", "start", "-a", "android.intent.action.MAIN",
                                  "-c", "android.intent.category.LAUNCHER", pkg])
            if success:
                return True
        return False
    except Exception:
        return False


def list_apps(index: dict, filter_str: str = None) -> list:
    apps = index.get("apps", [])
    if filter_str:
        filter_lower = filter_str.lower()
        apps = [a for a in apps if filter_lower in a["label"].lower() or filter_lower in a["pkg"].lower()]
    return sorted(apps, key=lambda x: x["label"].lower())
