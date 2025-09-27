# Super_Maro 

This is a tiny pygame runner demo. The player sprites were appearing too large; the game now scales them automatically.

How to run

1. Make sure Python and pygame are installed.
2. From the project directory run:

```powershell
python "c:\Super_Maro\main.py"
```

How to change player size

Open `main.py` and look at the top for these constants:

- `DEFAULT_PLAYER_RATIO` (default 0.25) — fraction of the window height used to compute the player height.
- `MIN_PLAYER_HEIGHT` — smallest allowed player height in pixels (prevent tiny sprites).
- `MAX_PLAYER_HEIGHT` — largest allowed player height (computed from window height).

By default the code computes PLAYER_HEIGHT = int(HEIGHT \* DEFAULT_PLAYER_RATIO) and then clamps it between the min and max values. You can change the ratio or the min/max to tune behavior.

Notes

Notes

- Images must be placed in the same directory: `run.png`, `jump.png`, `idle.png`.
- If an image file is missing the game will now create a simple placeholder so it won't crash. Replace placeholders with real art for best visuals.
- Obstacles are sized relative to the player so collision boxes and visuals stay consistent when you change player size.
