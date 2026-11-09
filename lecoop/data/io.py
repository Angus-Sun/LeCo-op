"""
using .npz file instead of one file per frame so training i/o is a lot more doable... 
supposedly... ig we'll see...
"""

from pathlib import Path
import numpy as np

def save_episode(path: Path, frames: np.ndarray, actions: np.ndarray) -> None:
    np.savez_compressed(path, frames=frames, actions=actions)

def load_episode(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(path)
    return data["frames"], data["actions"]
