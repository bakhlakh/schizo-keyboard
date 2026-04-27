"""
OS-level keyboard remapper using pynput.

Platform notes:
- Windows: works without admin rights (uses SetWindowsHookEx)
- Linux X11: requires user in 'input' group, or run with sudo
- Linux Wayland: not supported (pynput suppress unavailable)
"""

from __future__ import annotations
from pynput import keyboard as kb
from core.mapping import KeyMapping


class OSRemapper:
    def __init__(self, mapping: KeyMapping):
        self._mapping = mapping
        self._controller = kb.Controller()
        self._listener: kb.Listener | None = None
        self._injecting = False

    def start(self) -> None:
        if self._listener and self._listener.running:
            return
        self._listener = kb.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=True,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    @property
    def active(self) -> bool:
        return self._listener is not None and self._listener.running

    def _on_press(self, key) -> bool | None:
        if self._injecting:
            return True  # pass through our own injected events

        try:
            char = key.char
        except AttributeError:
            return True  # special key (shift, ctrl, etc.) — pass through

        if char and char.upper() in self._mapping.active_keys:
            mapped = self._mapping.get(char)
            out = mapped.lower() if char.islower() else mapped
            self._injecting = True
            try:
                self._controller.press(out)
            finally:
                self._injecting = False
            return False  # suppress original

        return True  # out-of-scope printable — pass through

    def _on_release(self, key) -> bool | None:
        if self._injecting:
            return True

        try:
            char = key.char
        except AttributeError:
            return True

        if char and char.upper() in self._mapping.active_keys:
            mapped = self._mapping.get(char)
            out = mapped.lower() if char.islower() else mapped
            self._injecting = True
            try:
                self._controller.release(out)
            finally:
                self._injecting = False
            return False

        return True
