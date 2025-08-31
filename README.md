# Flappy Bird Game

A small, polished Flappy Bird clone built with Python and pygame.
This repository contains a lightweight, well-documented example game intended for learning, packaging, and distribution.

---

## Project overview

- Language: Python 3
- Library: pygame
- Purpose: Educational game demonstrating simple game loop architecture, asset management, sound, and input handling.

This fork improves the original by:

- Using a bundled arcade-style TrueType font (`assets/PressStart2P-Regular.ttf`) for consistent UI rendering.
- Increasing screen resolution and scaling UI elements for readability.
- Adding a text-scaling helper to avoid clipping long UI strings.
- Providing a minimal headless smoke test for logic verification.

---

## Screenshot / Demo

Example:

```markdown
![Flappy Bird gameplay showing a pixelated yellow bird flying between green pipes with a blue sky background and score displayed at the top. The scene conveys a playful and challenging atmosphere typical of arcade games. The score text is visible in the upper center of the screen.](assets/Screenshot%202025-08-29%20234103.png)
```

---

## Requirements

- Python 3.8 or newer
- pygame (see `requirements.txt`)

---

## Install

Create a virtual environment (recommended) and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Run

Start the game from the repository root:

```powershell
python main.py
# or
python flappy.py
```

Controls

- SPACE: flap / jump
- Q or window close: quit

---

## Project layout

- `flappy.py` - Main game implementation (game loop, rendering, input).
- `main.py` - Canonical entry point that runs `flappy.main()`.
- `assets/` - Images, sounds, font, and highscore file (canonical asset location).
- `smoke_test.py` - Headless logic tests (non-GUI checks).
- `requirements.txt` - Project dependencies.
- `LICENSE` - MIT license.
- `README.md` - This file.

---

## Tests

Run the quick headless smoke test (no game window) to verify basic game logic:

```powershell
python smoke_test.py
```

Expected output: `SMOKE TEST PASSED`.

---

## Cleanup / Recommended gitignore

Canonical assets live in `assets/`. There may be duplicate audio/highscore files at the project root — you can safely remove them using the following PowerShell commands if you prefer a tidy repo:

```powershell
Remove-Item .\flap.wav -ErrorAction SilentlyContinue
Remove-Item .\point.wav -ErrorAction SilentlyContinue
Remove-Item .\hit.wav -ErrorAction SilentlyContinue
Remove-Item .\highscore.txt -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\__pycache__ -ErrorAction SilentlyContinue
```

A recommended `.gitignore` (already provided):

```
__pycache__/
*.pyc
.env
venv/
.DS_Store
```

---

## Contributing

Contributions are welcome. Typical workflow:

1. Fork the repository
2. Create a feature branch
3. Implement changes and add tests where feasible
4. Submit a pull request with a clear description of your changes

---

## Packaging / Distribution

For single-file distribution on Windows, you can use PyInstaller. Example (run after activating your virtualenv):

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Note: include the `assets/` directory when packaging the executable.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
