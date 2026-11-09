import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image
from lecoop.data.io import load_episode
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "dataset_check"

def main(episode_path: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(episode_path)
    frames, actions = load_episode(path)

    print(f"{path.name}")
    print(f"  frames: shape={frames.shape} dtype={frames.dtype}")
    print(f"  actions: shape={actions.shape} dtype={actions.dtype}")

    expected_frame_count = len(actions) + 1
    if len(frames) != expected_frame_count:
        print(f"  MISMATCH: expected {expected_frame_count} frames (len(actions)+1), got {len(frames)}")
    else:
        print("  frame/action count checks out (len(frames) == len(actions) + 1)")
    # 64x64 too small upscale so real eyes realize real lies (those who know)
    first = Image.fromarray(frames[0]).resize((512, 512), Image.NEAREST)
    last = Image.fromarray(frames[-1]).resize((512, 512), Image.NEAREST)
    first.save(OUT_DIR / f"{path.stem}_first.png")
    last.save(OUT_DIR / f"{path.stem}_last.png")
    print(f"  saved first/last frame (upscaled) to {OUT_DIR}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_dataset.py <path to episode .npz>")
        sys.exit(1)
    main(sys.argv[1])
