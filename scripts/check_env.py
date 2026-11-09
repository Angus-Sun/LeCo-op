"""Manual smoke test for lecoop.watch.env.FireboyWatergirlEnv: resets the
env, saves the first frame, takes a few random steps, saves the last frame.
Look at the saved PNGs to check reset() actually landed in gameplay (not a
menu) and that characters are visibly moving between the two screenshots.

Runs headless on purpose — a visible (headless=False) window showed visual
jitter that turned out to be a Chromium window-manager artifact, not a real
issue with the captured frame data (confirmed by tracing frame-to-frame
pixel diffs, which stayed small and steady throughout). Checking saved
frames is more reliable than watching the live window.

Usage: python scripts/check_env.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image

from lecoop.watch.env import FireboyWatergirlEnv

LEVEL_URL = "http://localhost:8765/games/1-forest-temple/index.html"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "env_check"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = FireboyWatergirlEnv(LEVEL_URL, headless=True)
    try:
        frame = env.reset()
        Image.fromarray(frame).save(OUT_DIR / "00_reset.png")
        print(f"Saved reset frame: {OUT_DIR / '00_reset.png'}")

        rng = np.random.default_rng(0)
        for i in range(20):
            actions = rng.integers(0, 2, size=(2, 3))
            frame, done = env.step(actions)
            if done:
                print(f"Episode ended at step {i}")
                break
        Image.fromarray(frame).save(OUT_DIR / "01_after_random_steps.png")
        print(f"Saved final frame: {OUT_DIR / '01_after_random_steps.png'}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
