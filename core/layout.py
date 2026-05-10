import sys
import subprocess

LAYOUTS: dict[str, list[list[str]]] = {
    "qwerty": [
        list("`1234567890-="),
        list("QWERTYUIOP[]\\"),
        list("ASDFGHJKL;'"),
        list("ZXCVBNM,./"),
    ],
    "azerty": [
        list("²&é\"'(-è_çà)="),
        list("AZERTYUIOP^$"),
        list("QSDFGHJKLMÙ*"),
        list("WXCVBN,;:!"),
    ],
    "qwertz": [
        list("^1234567890ß´"),
        list("QWERTZUIOPÜ+"),
        list("ASDFGHJKLÖÄ#"),
        list("YXCVBNM,.-"),
    ],
    "dvorak": [
        list("`1234567890[]"),
        list("',.PYFGCRL/=\\"),
        list("AOEUIDHTNS-"),
        list(";QJKXBMWVZ"),
    ],
    "colemak": [
        list("`1234567890-="),
        list("QWFPGJLUY;[]\\"),
        list("ARSTDHNEIO'"),
        list("ZXCVBKM,./"),
    ],
}


def get_rows() -> list[list[str]]:
    return LAYOUTS.get(_detect_name(), LAYOUTS["qwerty"])


def _detect_name() -> str:
    if sys.platform == "win32":
        return _from_windows()
    if sys.platform == "darwin":
        return _from_macos()
    return _from_linux()


def _from_windows() -> str:
    try:
        import ctypes
        hkl = ctypes.windll.user32.GetKeyboardLayout(0) & 0xFFFF
        return {0x040C: "azerty", 0x0407: "qwertz", 0x0807: "qwertz"}.get(hkl, "qwerty")
    except Exception:
        return "qwerty"


def _from_macos() -> str:
    try:
        out = subprocess.run(
            ["defaults", "read", "/Library/Preferences/com.apple.HIToolbox",
             "AppleCurrentKeyboardLayoutInputSourceID"],
            capture_output=True, text=True, timeout=2,
        ).stdout.strip().lower()
        for keyword, name in [
            ("azerty", "azerty"), ("french", "azerty"),
            ("dvorak", "dvorak"), ("colemak", "colemak"),
            ("german", "qwertz"),
        ]:
            if keyword in out:
                return name
    except Exception:
        pass
    return "qwerty"


def _from_linux() -> str:
    try:
        out = subprocess.run(
            ["setxkbmap", "-query"], capture_output=True, text=True, timeout=2,
        ).stdout
        info: dict[str, str] = {
            k.strip(): v.strip()
            for line in out.splitlines()
            if ":" in line
            for k, _, v in [line.partition(":")]
        }
        layout = info.get("layout", "")
        variant = info.get("variant", "")
        if layout == "fr":
            return "azerty"
        if layout in ("de", "ch"):
            return "qwertz"
        if "dvorak" in variant or layout == "dvorak":
            return "dvorak"
        if "colemak" in variant:
            return "colemak"
    except Exception:
        pass
    return "qwerty"
