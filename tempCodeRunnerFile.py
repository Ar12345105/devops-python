# sysinfo.py
# Minimal DevOps helper script

import os
import json
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import yaml
 

# --- Read config.yaml ---
CONFIG_FILE = ROOT / "config.yaml"
if CONFIG_FILE.exists():
    with CONFIG_FILE.open("r") as f:
        config = yaml.safe_load(f)
else:
    config = {"disk_alert_percent": 20}  # default if YAML missing

# --- Setup paths ---
ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "devops_log.txt"
STATUS_JSON = ROOT / "status.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(line: str) -> None:
    """Append timestamped line to log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {line}\n")

def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    """Run a system command safely"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

# --- Collect system info ---
system = platform.system()
release = platform.release()
python_ver = platform.python_version()

du = shutil.disk_usage("/")  
disk_info = {
    "total_gb": round(du.total / (1024**3), 2),
    "used_gb": round((du.total - du.free) / (1024**3), 2),
    "free_gb": round(du.free / (1024**3), 2),
    "free_percent": round(du.free / du.total * 100, 2)
}

if system == "Windows":
    cmd = ["cmd", "/c", "systeminfo"]
else:
    cmd = ["uname", "-a"]

rc, out, err = run_cmd(cmd)

status = {
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "system": system,
    "release": release,
    "python": python_ver,
    "disk": disk_info,
    "command_run": " ".join(cmd),
    "command_return_code": rc,
    "command_stdout_preview": out[:500],
    "command_stderr_preview": err[:500]
}

# --- Write outputs ---
log(f"Sysinfo collected on {system} {release} | Python {python_ver} | Disk free {disk_info['free_percent']}%")

with STATUS_JSON.open("w", encoding="utf-8") as f:
    json.dump(status, f, indent=2)

print("✅ Sysinfo captured.")
print(f"   Log:    {LOG_FILE}")
print(f"   Status: {STATUS_JSON}")

