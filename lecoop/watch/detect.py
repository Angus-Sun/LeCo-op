"""
Detection to see if death or level complete screen is up from the game frame 
so the watch phase knows when to reset

Calibrated the values to some screenshots I took of the game running ONLY in forest
temple. Surely this won't come back and bite me in the butt :D 

Detects the 'episode over' overlay (death / level-complete screens) from a
raw game frame, so the Watch phase knows when to reset.

I found that the win/death panel read 139-142 usually mean brightness in center crop
while it was ~45 during gameplay 
"""

import numpy as np
CENTER_CROP = 0.5
# threshold for deciding between not an "episode over" screen and is on "episode over" screen
MIN_BRIGHTNESS = 90.0

def _center_crop(frame: np.ndarray, frac: float) -> np.ndarray:
    h, w = frame.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    top = (h - ch) // 2
    left = (w - cw) // 2
    return frame[top : top + ch, left: left + cw]

def is_episode_over(frame: np.ndarray) -> bool:
    crop = _center_crop(frame, CENTER_CROP)
    brightness = crop.mean()
    return brightness > MIN_BRIGHTNESS