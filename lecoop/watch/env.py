"""
actions are [2,3] (both players don't need the down key since game doesn't make them use it)
also made buttons held between steps instead of just tapped so there's actual movement happening

since level JSON is fetched by the game as a live network request, 
I was able to intercept the request with page.route() and served a modified
copy with different chars spawn coordinates 

MECHANIC_SPAWNS stores useful coordinates of areas next to areas of interest that the AI should
learn the behaviour of
"""

import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from lecoop.watch.detect import is_episode_over

PLAYER_KEYS = [
    ["ArrowUp", "ArrowLeft", "ArrowRight"],  # fireboy
    ["w", "a", "d"],  # watergirl
]

STEP_DELAY_MS = 50
START_GAME_BUTTON = (640, 408)
FIRST_LEVEL_NODE = (640, 618)

LEVEL_JSON_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "game" / "games" / "1-forest-temple" / "data" / "tutorials" / "levels" / "forest_01.json"
)
LEVEL_JSON_URL_MATCH = "forest_01.json"
# fireboy and watergirl are both near the same hazard but offset
# slightly so the two characters don't spawn exactly on top of each other
MECHANIC_SPAWNS = {
    "lava": ((512, 896), (552, 896)),
    "water": ((992, 896), (1032, 896)),
    "toxic_pool": ((704, 704), (744, 704)),
}

class FireboyWatergirlEnv:
    def __init__(self, level_url: str, headless: bool = False, viewport: tuple[int, int] = (1280, 720)):
        self.level_url = level_url
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._page = self._browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        self._held = [[False] * 3, [False] * 3]
        self._pending_spawn = None  
        self._page.route("**/*", self._handle_route)

    def _handle_route(self, route) -> None:
        if LEVEL_JSON_URL_MATCH not in route.request.url or self._pending_spawn is None:
            route.continue_()
            return
        fireboy_xy, watergirl_xy = MECHANIC_SPAWNS[self._pending_spawn]
        with open(LEVEL_JSON_PATH, encoding="utf-8") as f:
            level = json.load(f)
        for layer in level["layers"]:
            if layer["name"] == "Chars":
                for obj in layer["objects"]:
                    if obj.get("gid") == 16:
                        obj["x"], obj["y"] = fireboy_xy
                    elif obj.get("gid") == 17:
                        obj["x"], obj["y"] = watergirl_xy
        route.fulfill(status=200, content_type="application/json", body=json.dumps(level))

    def _screenshot(self) -> np.ndarray:
        png_bytes = self._page.screenshot()
        img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        return np.array(img)

    def _wait_for_camera_settle(
        self,
        max_checks: int = 20,
        poll_ms: int = 100,
        stable_threshold: float = 0.5,
        required_stable_checks: int = 3,
    ) -> np.ndarray:
        frame = self._screenshot()
        prev_brightness = frame.mean()
        stable_count = 0
        for _ in range(max_checks):
            self._page.wait_for_timeout(poll_ms)
            frame = self._screenshot()
            brightness = frame.mean()
            if abs(brightness - prev_brightness) < stable_threshold:
                stable_count += 1
                if stable_count >= required_stable_checks:
                    return frame
            else:
                stable_count = 0
            prev_brightness = brightness
        return frame

    def _release_all_keys(self) -> None:
        for player_keys, held in zip(PLAYER_KEYS, self._held):
            for key, is_held in zip(player_keys, held):
                if is_held:
                    self._page.keyboard.up(key)
        self._held = [[False] * 3, [False] * 3]

    def reset(self, spawn: str | None = None) -> np.ndarray:
        """
        spawn is decided to be defvault if it's None but use a key from MECHANIC_SPAWNS
        to spawn near whatever hazard is chosen instead
        """
        if spawn is not None and spawn not in MECHANIC_SPAWNS:
            raise ValueError(f"unknown spawn {spawn!r}, expected one of {list(MECHANIC_SPAWNS)}")
        self._pending_spawn = spawn
        self._release_all_keys()
        self._page.goto(self.level_url)
        self._page.wait_for_timeout(2000)
        self._page.mouse.click(*START_GAME_BUTTON)
        self._page.wait_for_timeout(1500)
        self._page.mouse.click(*FIRST_LEVEL_NODE)
        self._page.wait_for_timeout(500)
        return self._wait_for_camera_settle()

    def step(self, actions: np.ndarray) -> tuple[np.ndarray, bool]:
        """actions: [2, 3] array, 0/1 per button and returns (frame, done)."""
        for player_idx, player_keys in enumerate(PLAYER_KEYS):
            for button_idx, key in enumerate(player_keys):
                want_held = bool(actions[player_idx, button_idx])
                is_held = self._held[player_idx][button_idx]
                if want_held and not is_held:
                    self._page.keyboard.down(key)
                elif is_held and not want_held:
                    self._page.keyboard.up(key)
                self._held[player_idx][button_idx] = want_held

        self._page.wait_for_timeout(STEP_DELAY_MS)
        frame = self._screenshot()
        done = is_episode_over(frame)
        if done:
            self._release_all_keys()
        return frame, done

    def close(self) -> None:
        self._release_all_keys()
        self._browser.close()
        self._playwright.stop()
