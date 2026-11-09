"""
script to collect data of the full episode runs for training later on
"""

from pathlib import Path

import numpy as np
from PIL import Image

from lecoop.data.io import save_episode
from lecoop.watch.env import MECHANIC_SPAWNS, FireboyWatergirlEnv
from lecoop.watch.policy import StickyRandomPolicy

FRAME_SIZE = (64, 64)
MAX_STEPS_PER_EPISODE = 500  # safety cap in case an episode never naturally ends

# None = default entrance. Equal chance of entrance vs. each mechanic spawn.
SPAWN_CHOICES = [None, *MECHANIC_SPAWNS.keys()]

def _downsample(frame: np.ndarray) -> np.ndarray:
    img = Image.fromarray(frame).resize(FRAME_SIZE, Image.BILINEAR)
    return np.array(img)

def collect_episode(env: FireboyWatergirlEnv, policy: StickyRandomPolicy, spawn: str | None) -> tuple[np.ndarray, np.ndarray]:
    """
    from my understanding, frames has one more entry than actions so frames[0] is the reset frame
    frames[t+1] is the result of actions[t] and this function returns (frames, actions)
    """

    frame = env.reset(spawn=spawn)
    frames = [_downsample(frame)]
    actions = []

    for i in range(MAX_STEPS_PER_EPISODE):
        action = policy.next_actions()
        frame, done = env.step(action)
        actions.append(action)
        frames.append(_downsample(frame))
        if done:
            break

    return np.stack(frames), np.stack(actions)

def collect_episodes(env: FireboyWatergirlEnv, out_dir: Path, num_episodes: int, seed: int = 0) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    for i in range(num_episodes):
        spawn = rng.choice(SPAWN_CHOICES)
        policy = StickyRandomPolicy(rng)
        frames, actions = collect_episode(env, policy, spawn)
        path = out_dir / f"episode_{i:05d}.npz"
        save_episode(path, frames, actions)
        print(f"saved {path} ({len(actions)} steps) spawn={spawn}")
