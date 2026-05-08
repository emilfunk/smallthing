# macOS Permissions Required for Charmstone

Charmstone.app requires two macOS permission grants before it can function.
Both are found under **System Settings → Privacy & Security**.

---

## 1. Accessibility

**Required for:** global hotkey registration via pynput.

### Steps
1. Open **System Settings** → **Privacy & Security** → **Accessibility**.
2. Click the **+** button and add `Charmstone.app` (or your Python interpreter
   during development).
3. Ensure the toggle next to Charmstone is **on**.

> Without Accessibility permission, `pynput.keyboard.GlobalHotKeys` will silently
> fail to capture keystrokes because macOS blocks event-tap creation for
> unauthorised processes.

---

## 2. Automation (AppleScript / Finder)

**Required for:** reading the selected folder path from Finder via `osascript`.

### Steps
1. Open **System Settings** → **Privacy & Security** → **Automation**.
2. Expand **Charmstone** (or `Python` / `osascript` during development).
3. Enable the toggle next to **Finder**.

> On first launch, macOS will display a prompt asking "Charmstone wants to
> control Finder." Click **OK** to grant access. If you clicked **Don't Allow**,
> reset it via the Automation pane above.

---

## 3. Docker

Charmstone orchestrates a Docker sandbox. Ensure Docker Desktop (or
equivalent) is installed and the Docker daemon is running before invoking
"Initialize Sandbox" from the radial menu.

---

## 4. Building from source (development)

```bash
cd charmstone
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run directly (grant permissions to the Python binary inside .venv):
python main.py
```

## 5. Building the .app bundle

```bash
pip install pyinstaller
pyinstaller charmstone.spec
# Output: dist/Charmstone.app
open dist/Charmstone.app
```

After building, grant Accessibility and Automation permissions to
`dist/Charmstone.app` as described above. The bundled app uses an embedded
Python interpreter, so permissions granted to the raw `python` binary will
**not** carry over automatically.
