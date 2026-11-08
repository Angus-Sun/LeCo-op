#script for testing how accurate detector is for images of actual game

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image

from lecoop.watch.detect import MIN_BRIGHTNESS, _center_crop, is_episode_over

def main(paths: list[str]) -> None:
    for p in paths:
        img = np.array(Image.open(p).convert("RGB"))
        crop = _center_crop(img, 0.5)
        brightness = crop.mean()
        verdict = is_episode_over(img)
        print(f"{p}: brightness={brightness:.2f} (threshold={MIN_BRIGHTNESS}) -> episode_over={verdict}")

if __name__ == "__main__":
    main(sys.argv[1:])
