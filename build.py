import subprocess
import platform
import os
import shutil  # Added for directory removal
from pathlib import Path

# --- THE SINGLE SOURCE OF TRUTH ---
# 1. Change this name to change the EXE name AND the config it looks for
CONFIG_FILE_NAME = "launch-script-lms-sample"

# 2. Paths (Relative to this Root-level build.py)
INTERNAL_JSON = Path(f"configs/{CONFIG_FILE_NAME}.json") 
MAIN_SCRIPT = Path("src/main.py")
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")    # Added for cleanup
SPEC_FILE = Path(f"{CONFIG_FILE_NAME}.spec") # Added for cleanup

def get_icon_path():
    """Checks for fixed icon.ico or icon.icns files in the root folder only."""
    os_type = platform.system()
    # Use .ico for Windows, .icns for macOS
    target_ext = ".ico" if os_type == "Windows" else ".icns"
    icon_name = f"icon{target_ext}"
    
    icon_path = Path(icon_name)
    
    if icon_path.exists():
        print(f"🎨 Icon Found in root: {icon_path}")
        return str(icon_path)
            
    print("ℹ️ No icon.ico/icns found in root (using system default).")
    return None

def cleanup():
    """Removes temporary build artifacts."""
    print("🧹 Cleaning up temporary build files...")
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  - Removed {BUILD_DIR}/")
        
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"  - Removed {SPEC_FILE}")

def build():
    os_type = platform.system()
    # Use ; for Windows and : for Mac/Linux
    sep = ";" if os_type == "Windows" else ":"
    
    if not INTERNAL_JSON.exists():
        print(f"❌ Error: Could not find configuration at {INTERNAL_JSON}")
        return

    if not MAIN_SCRIPT.exists():
        print(f"❌ Error: Could not find source code at {MAIN_SCRIPT}")
        return

    # We bundle the JSON into the root of the EXE with its specific name
    # The dot (.) at the end tells PyInstaller to put it in the bundle's root
    add_data_flag = f"{INTERNAL_JSON}{sep}."

    cmd = [
        "uv", "run", "pyinstaller",
        "--onefile",
        "--noconfirm",
        "--clean", # Added: Clears PyInstaller cache before building
        "--add-data", add_data_flag,
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR), # Explicitly set build folder
        "--name", CONFIG_FILE_NAME,
    ]

    # --- APPLY ICON FROM ROOT ---
    icon_path = get_icon_path()
    if icon_path:
        cmd.extend(["--icon", icon_path])

    cmd.append(str(MAIN_SCRIPT))

    print(f"🚀 Building [{CONFIG_FILE_NAME}]...")
    print(f"📦 Bundling: {INTERNAL_JSON}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✅ Build Successful!")
        print(f"📂 Executable: {DIST_DIR}/{CONFIG_FILE_NAME}" + (".exe" if os_type == "Windows" else ""))
        cleanup() # Run cleanup after success
    else:
        print("\n❌ Build Failed. Keeping logs for debugging.")

if __name__ == "__main__":
    build()