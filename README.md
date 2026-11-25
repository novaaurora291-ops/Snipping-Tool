# Snipping Tool

A small Windows screen snipping tool (Python + PySide6).

## Planned features
- Rectangle capture: drag a rectangle over a frozen screenshot; Esc cancels.
- Preview: the captured image in a preview window.
- Copy: put the capture on the clipboard.
- Save PNG: save the capture as a .png file.
- Main window with a New Snip button that starts a capture and opens the preview.

## Run from source
```
pip install -r requirements.txt
python run.py
```

## Branches
- `main`: reviewed code only.
- `agent-*`: one branch (and git worktree) per worker.
- `integration`: workers' branches merged for the live Windows test before review.
