import threading
from pynput import keyboard
from src.config import Config

class HotkeyListener:
    def __init__(self, on_start_callback, on_stop_callback):
        self.on_start = on_start_callback
        self.on_stop = on_stop_callback
        self.mode = Config.MODE
        self.hotkey_name = Config.HOTKEY
        self.is_active = False
        self._listener = None
        self._target_key = self._resolve_target_key(self.hotkey_name)

    def _resolve_target_key(self, name: str):
        key_map = {
            "f8": keyboard.Key.f8,
            "f9": keyboard.Key.f9,
            "f10": keyboard.Key.f10,
            "f12": keyboard.Key.f12,
            "scroll_lock": keyboard.Key.scroll_lock,
            "caps_lock": keyboard.Key.caps_lock,
        }
        return key_map.get(name.lower(), keyboard.Key.f8)

    def _on_press(self, key):
        if key == self._target_key:
            if self.mode == "push_to_talk":
                if not self.is_active:
                    self.is_active = True
                    threading.Thread(target=self.on_start, daemon=True).start()
            elif self.mode == "toggle":
                if not self.is_active:
                    self.is_active = True
                    threading.Thread(target=self.on_start, daemon=True).start()
                else:
                    self.is_active = False
                    threading.Thread(target=self.on_stop, daemon=True).start()

    def _on_release(self, key):
        if key == self._target_key:
            if self.mode == "push_to_talk":
                if self.is_active:
                    self.is_active = False
                    threading.Thread(target=self.on_stop, daemon=True).start()

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
