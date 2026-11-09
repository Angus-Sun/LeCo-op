import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lecoop.watch.collect import collect_episodes
from lecoop.watch.env import FireboyWatergirlEnv

LEVEL_URL = "http://localhost:8765/games/1-forest-temple/index.html"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def main() -> None:
    num_episodes = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    env = FireboyWatergirlEnv(LEVEL_URL, headless=True)
    try:
        collect_episodes(env, OUT_DIR, num_episodes)
    finally:
        env.close()

if __name__ == "__main__":
    main()
