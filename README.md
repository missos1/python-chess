# Python Chess
Chess game created with Python and Pygame.

## UCI match test (CuteChess)

This repository includes a UCI wrapper at the repo root: `uci.py`. It can load either
the current bot package or an older snapshot by passing `--package`.

### Requirements
- CuteChess CLI installed (path to `cutechess-cli.exe`).
- Python available (the same interpreter used for your project).
- Old bot snapshot folder: `data/classes/chess_bot_v1` (copy from `data/classes/chess_bot`).

### Command (10 games)
Replace the CuteChess and Python paths with your own if needed.

```powershell
& "E:\\Workspace\\Project\\ChessAI_VNU\\Cute Chess\\cutechess-cli.exe" `
	-engine name="NewBot" cmd="E:\\Python\\Python314\\python.exe" arg="E:\\Workspace\\Project\\ChessAI_VNU\\uci.py" arg="--package" arg="data.classes.chess_bot" dir="E:\\Workspace\\Project\\ChessAI_VNU" `
	-engine name="OldBot" cmd="E:\\Python\\Python314\\python.exe" arg="E:\\Workspace\\Project\\ChessAI_VNU\\uci.py" arg="--package" arg="data.classes.chess_bot_v1" dir="E:\\Workspace\\Project\\ChessAI_VNU" `
	-each proto=uci tc=5+0.1 -games 10 -concurrency 2
```

### Command with random opening from output.txt
If `output.txt` contains alternating lines of opening name and FEN, create a FEN-only file first:

```powershell
@'
from pathlib import Path

repo_root = Path(r"E:\\Workspace\\Project\\ChessAI_VNU")
input_path = repo_root / "output.txt"
output_path = repo_root / "openings_fen.txt"

with input_path.open("r", encoding="utf-8", errors="replace") as f:
	lines = [line.strip() for line in f if line.strip()]

fens = [lines[i] for i in range(1, len(lines), 2)]
output_path.write_text("\n".join(fens) + "\n", encoding="utf-8")
print(f"Wrote {len(fens)} FEN lines to {output_path}")
'@ | & "E:\\Workspace\\Project\\ChessAI_VNU\\.venv\\Scripts\\python.exe" -
```

Then run CuteChess using a random opening from that file:

```powershell
& "E:\\Workspace\\Project\\ChessAI_VNU\\Cute Chess\\cutechess-cli.exe" `
	-engine name="NewBot" cmd="E:\\Python\\Python314\\python.exe" arg="E:\\Workspace\\Project\\ChessAI_VNU\\uci.py" arg="--package" arg="data.classes.chess_bot" dir="E:\\Workspace\\Project\\ChessAI_VNU" `
	-engine name="OldBot" cmd="E:\\Python\\Python314\\python.exe" arg="E:\\Workspace\\Project\\ChessAI_VNU\\uci.py" arg="--package" arg="data.classes.chess_bot_v1" dir="E:\\Workspace\\Project\\ChessAI_VNU" `
	-each proto=uci tc=5+0.1 -openings file="E:\\Workspace\\Project\\ChessAI_VNU\\openings_fen.txt" format=epd order=random -games 10 -concurrency 2
```


### What the result means
- The match summary prints NewBot vs OldBot with wins, losses, and draws.
- Increase `-games` and `tc` for more reliable results.
