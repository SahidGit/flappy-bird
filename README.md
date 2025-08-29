# Flappy Bird - Improved (Python + pygame)

This is a small Flappy Bird clone implemented in Python using pygame. I updated the project to:

- Use the bundled TTF font (`assets/PressStart2P-Regular.ttf`) for all UI text via `pygame.font.Font`.
- Increase the window resolution and scale UI elements (titles, score, pipes, bird) for better visibility.
- Clean up minor formatting and indentation issues in `flappy.py` and ensured the script is syntax-correct.

## Run the game

Requirements:

- Python 3.8+
- pygame

Install and run:

```powershell
python -m pip install --upgrade pip
pip install pygame
python flappy.py
```

## What changed (high level)

- Font integration: the game now uses `assets/PressStart2P-Regular.ttf` if present. The font is loaded with `pygame.font.Font(path, size)` via a small helper `load_font(size)` so different UI sizes render correctly.
- Window and UI scaling: `WIDTH` and `HEIGHT` increased to 540x760. Fonts and sprites were scaled to keep proportions.
- Minor refactors: cleaned up unused imports and fixed indentation issues in `Bird.__init__`.

## Cleanup note

Canonical assets are stored in `assets/`. There are some duplicate files in the project root (audio files and `highscore.txt`) that can be removed. They are not used by the game because `flappy.py` reads from `assets/`.

Recommended cleanup commands (PowerShell):

```powershell
Remove-Item .\flap.wav -ErrorAction SilentlyContinue
Remove-Item .\point.wav -ErrorAction SilentlyContinue
Remove-Item .\hit.wav -ErrorAction SilentlyContinue
Remove-Item .\highscore.txt -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\__pycache__ -ErrorAction SilentlyContinue
```

## Publish to GitHub

I can't push to your GitHub repository directly. To publish this project under your account (https://github.com/SahidGit) do the following in PowerShell from the project root:

```powershell
git init
git add .
git commit -m "Initial Flappy Bird - Improved"
# Create a repo on GitHub web UI (e.g. SahidGit/flappy-bird) then:
git remote add origin https://github.com/SahidGit/flappy-bird.git
git branch -M main
git push -u origin main
```

If you want I can prepare a small `publish.ps1` script that automates the push once you've created the remote repo and set your credentials.

## Notes and follow-ups

- I validated the code for syntax errors and adjusted UI positions; I could not run an automated in-window test from this environment. Please run `python flappy.py` locally and verify that:
  - Bird jumps with SPACE
  - Pipes spawn and move left
  - Score increases when passing pipes
  - Collisions trigger game over and highscore persists

If you want, I can also prepare a `requirements.txt` and a PyInstaller spec for packaging.

Enjoy!
