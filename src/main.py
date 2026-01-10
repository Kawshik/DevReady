import subprocess
import platform
import webbrowser
import time
import os
import sys
import json
import urllib.request
from pathlib import Path

def get_base_path():
    """Returns the path to the directory containing the executable or script."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def get_config_path(config_arg=None):
    """
    Filename-Aware Discovery:
    1. CLI Argument: Explicitly provided file.
    2. Linked Side-car: Looks for [MyName].json next to the EXE.
    3. Linked Internal: Looks for [MyName].json inside the bundle.
    """
    # 1. Check CLI Argument
    if config_arg:
        arg_path = get_base_path() / config_arg
        if arg_path.exists():
            return arg_path

    # Get the name of this running application (e.g., 'lms')
    app_name = Path(sys.executable).stem if getattr(sys, 'frozen', False) else Path(__file__).stem
    target_json = f"{app_name}.json"

    # 2. Check for an external match (Side-car)
    external_path = get_base_path() / target_json
    if external_path.exists():
        print(f"📂 Loading External Config: {target_json}")
        return external_path

    # 3. Check Internal Bundle (Built by build.py)
    if getattr(sys, 'frozen', False):
        internal_path = Path(sys._MEIPASS) / target_json
        if internal_path.exists():
            print(f"📦 Loading Bundled Config: {target_json}")
            return internal_path

    return None

def kill_process_on_port(port):
    os_type = platform.system()
    try:
        if os_type == "Windows":
            cmd = f'netstat -ano | findstr LISTENING | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            for line in output.strip().split('\n'):
                if line.strip():
                    pid = line.strip().split()[-1]
                    print(f"💀 Killing port {port} (PID: {pid})...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        else:
            cmd = f'lsof -t -i:{port}'
            pid = subprocess.check_output(cmd, shell=True).decode().strip()
            if pid:
                subprocess.run(f'kill -9 {pid}', shell=True)
    except Exception:
        pass

def wait_for_health_check(url, timeout=30):
    print(f"🔍 Health check: {url}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.getcode() == 200:
                    print(f"✅ Service Online")
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def run_task(task, os_type, cursor_bin):
    print(f"\n🚀 TASK: {task['name']}")
    
    # TERMINAL ACTION
    if task.get("action") == "terminal":
        if task.get("port"):
            kill_process_on_port(task["port"])
        
        path = Path(task["path"])
        if not path.exists():
            print(f"❌ Error: Path does not exist -> {path}")
            return

        cmd = task["command"]
        if os_type == "Windows":
            subprocess.Popen(f'start "{task["name"]}" cmd /K "cd /d {path} && {cmd}"', shell=True)
        elif os_type == "Darwin":
            subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "cd {path} && {cmd}"'])
        
        if task.get("cursor"):
            subprocess.Popen([cursor_bin, str(path)], shell=(os_type == "Windows"))
            
        if task.get("health_check"):
            wait_for_health_check(task["health_check"])

    # BROWSER ACTION
    elif task.get("action") == "browser":
        time.sleep(task.get("delay", 0))
        print(f"🌐 Opening: {task['url']}")
        webbrowser.open(task["url"])

if __name__ == "__main__":
    # Check for CLI arg, otherwise use None
    cmd_arg = sys.argv[1] if len(sys.argv) > 1 else None
    config_path = get_config_path(cmd_arg)

    if not config_path:
        app_name = Path(sys.executable).stem if getattr(sys, 'frozen', False) else "main"
        print(f"❌ CRITICAL ERROR: Could not find {app_name}.json")
        print(f"Please ensure the JSON matches the name of the executable.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            
        os_platform = platform.system()
        cursor_exe = data.get("cursor_bin", "cursor")
        
        for task in data.get("tasks", []):
            run_task(task, os_platform, cursor_exe)
            
        print("\n✅ All tasks initiated successfully.")
        time.sleep(2)
        
    except Exception as e:
        print(f"💥 Runtime Error: {e}")
        input("\nPress Enter to exit...")