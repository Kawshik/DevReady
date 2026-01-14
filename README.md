# 🚀 DevReady

DevReady is a professional, filename-aware automation engine designed to launch full-stack development environments with a single click. It synchronizes Port Killing, Health Checks, IDE Integration (Cursor), and Web Browser automation into a unified workflow.

---

## 📂 Project Structure

```text
DevReady/
├── build.py            # The Root-level build script
├── configs/
│   └── lms.json        # Your configuration file
├── src/
│   └── main.py         # The core logic
├── dist/               # Output folder for the EXE
├── build/              # (Temporary) Created during build, then auto-deleted
├── pyproject.toml      # Managed by uv
└── LICENSE             <-- LICENSE file
```

## ⚙️ Configuration (JSON Schema)

DevReady uses **Smart Discovery** to find its configuration based on its own filename. If the executable is named `lms.exe`, it looks for:

1.  **CLI Argument:** (e.g., `lms.exe custom.json`)
2.  **External Side-car:** A file named `lms.json` sitting in the same folder as the `.exe`.
3.  **Internal Bundle:** The `lms.json` packaged inside the `.exe` during build.

### Schema Example: `configs/lms.json`

```json
{
    "cursor_bin": "cursor",
    "tasks": [
        {
            "name": "Backend",
            "path": "C:/Users/username/Desktop/Work/Api Gateway",
            "action": "terminal",
            "command": "uv run uvicorn app:app --reload",
            "port": 8000,
            "cursor": true,
            "health_check": "[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)",
            "terminal_settings": {
                "mode": "integrated"
            }
        },
        {
            "name": "Frontend",
            "action": "browser",
            "url": "http://localhost:4321",
            "delay": 1
        }
    ]
}
```


### Task Attributes

| Attribute | Type | Description |
| :--- | :--- | :--- |
| **name** | `string` | Display name in the logs. |
| **action** | `string` | `terminal` or `browser`. |
| **path** | `string` | **(Terminal)** Absolute path to the project directory. |
| **command** | `string` | **(Terminal)** The shell command to run (e.g., `uv run uvicorn...`). |
| **port** | `int` | *(Optional)* Port to kill before launching to avoid conflicts. |
| **health_check** | `string` | *(Optional)* URL to ping. Waits for `200 OK` before proceeding. |
| **cursor** | `bool` | If `true`, opens the folder in Cursor. |
| **terminal_settings** | `object` | *(Optional)* Use `{"mode": "integrated"}` to run inside Cursor. |
| **url** | `string` | **(Browser)** The website to open. |
| **delay** | `int` | **(Browser)** Seconds to wait before opening. |


## 🛠️ Getting Started

Follow these steps to set up **DevReady** on your local machine.

### 1. Prerequisites
This project uses **uv** for ultra-fast dependency management. If you don't have it installed:

* **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
* **macOS/Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 2. Clone and Initialize
```bash
# Clone the repository
git clone <your-repo-url>
cd DevReady

# Synchronize dependencies and virtual environment
uv sync
```
### 3. Create Your Configuration
Since local paths vary by machine, configuration files are excluded from Git.

1. Navigate to the `configs/` folder.
2. Create a file named `YOUR-FILE-NAME.json`.
3. Use the template provided in the documentation, replacing the `path` attributes with your local project directories.

### 4. Build the Executable
Run the build script to generate your portable launcher. This will package your `YOUR-FILE-NAME.json` inside the executable.

```bash
uv run build.py
```
### 5. Launch
Your compiled tool is now ready in the `dist/` folder:

* **Windows:** `dist/YOUR-FILE-NAME.exe`
* **macOS/Linux:** `./dist/YOUR-FILE-NAME`


## 🖱️ Usage

### One-Click Launch
Double-click the generated `.exe` in the `dist/` folder. It will automatically load the internal `dev_setup.json` that was packaged during the build.

### Hot-Swapping Config (Side-car)
To change settings without re-building the code, simply place a JSON file with the same name as the executable (e.g., `lms.json`) next to the `.exe`. DevReady will prioritize this external file.

## 🖥️ Integrated Terminal Support

When `terminal_settings: {"mode": "integrated"}` is used, DevReady performs a **Smart Merge**:

1. **Discovery:** It checks for an existing `.vscode/tasks.json` in your project path.
2. **Comment-Safe Parsing:** It can read user files even if they contain `//` comments.
3. **Non-Destructive Merge:** It adds or updates a task named `DevReady: [Task Name]` while leaving your existing manual tasks untouched.
4. **Fingerprinting:** Every generated task is tagged with `"origin": "devready"`, allowing the engine to distinguish its tasks from yours.
5. **Auto-Run:** Tasks are configured with `runOn: folderOpen`, so they trigger as soon as Cursor launches.

## ⚠️ Important Notes

* **Path Formatting:** Always use **forward slashes** (`/`) in your JSON configuration (e.g., `C:/Projects/App`). Backslashes (`\`) are escape characters in JSON and will cause the configuration to fail.
* **Port Management:** The script will attempt to force-close any process currently using the ports specified in your config. This prevents "Address already in use" errors when restarting your environment.
* **Integrated Mode Logic:** In `integrated` mode, the script skips opening an external OS terminal and hands the command off to Cursor's internal panel.
* **Smart Cleanup:** The `build.py` script automatically removes build artifacts after a successful run to keep your repository root clean.
* **Cursor Integration:** To use the `cursor: true` feature, ensure the Cursor CLI is installed.
    * *How:* Open Cursor, press `Ctrl+Shift+P`, and run **"Shell Command: Install 'cursor' command in PATH"**.
* **Permissions:** You may need to run the executable with sufficient privileges if the ports you are trying to clear are being held by system-level processes.
* **Executable Portability:** The tool uses `sys._MEIPASS` to resolve internal paths, meaning you can move the `.exe` to any folder on your computer and it will still function correctly.
* **Filename Matching:** The executable name and the JSON filename must match for the auto-discovery to work.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.