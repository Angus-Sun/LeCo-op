"""smoke test script that prints whenever the action combo actually changes to see if
it's holding each combo for 10-40 steps instead of flipping every step
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image

from lecoop.watch.env import FireboyWatergirlEnv
from lecoop.watch.policy import StickyRandomPolicy

LEVEL_URL = "http://localhost:8765/games/1-forest-temple/index.html"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "policy_check"
NUM_STEPS = 100
SAVE_EVERY = 20

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    policy = StickyRandomPolicy(rng)

    env = FireboyWatergirlEnv(LEVEL_URL, headless=True)
    try:
        frame = env.reset()
        Image.fromarray(frame).save(OUT_DIR / "step_000.png")

        prev_actions = None
        for i in range(1, NUM_STEPS + 1):
            actions = policy.next_actions()
            if prev_actions is None or not np.array_equal(actions, prev_actions):
                print(f"step {i:3d}: new combo -> {actions.tolist()}")
            prev_actions = actions

            frame, done = env.step(actions)
            if done:
                print(f"episode ended at step {i}")
                break
            if i % SAVE_EVERY == 0:
                Image.fromarray(frame).save(OUT_DIR / f"step_{i:03d}.png")
    finally:
        env.close()

if __name__ == "__main__":
    main()
