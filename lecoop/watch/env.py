"""
actions are [2,3] (both players don't need the down key since game doesn't make them use it)
also made buttons held between steps instead of just tapped so there's actual movement happening
"""

import io

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

class FireboyWatergirlEnv:
    def __init__(self, level_url: str, headless: bool = True, viewport: tuple[int, int] = (1280, 720)):
        self.level_url = level_url
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._page = self._browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        self._held = [[False] * 3, [False] * 3]

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

    def reset(self) -> np.ndarray:
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
