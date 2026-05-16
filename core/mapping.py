import random
import hashlib


SCOPE_LETTERS         = 'letters'
SCOPE_LETTERS_NUMBERS = 'letters_numbers'
SCOPE_ALL_PRINTABLE   = 'all_printable'

_LETTERS     = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
_NUMBERS     = list('1234567890')
_PUNCTUATION = list("`-=[]\\;',./")  # 11 physical unshifted keys only

_SCOPE_KEYS = {
    SCOPE_LETTERS:         _LETTERS,
    SCOPE_LETTERS_NUMBERS: _LETTERS + _NUMBERS,
    SCOPE_ALL_PRINTABLE:   _LETTERS + _NUMBERS + _PUNCTUATION,
}


class KeyMapping:
    def __init__(self, scope: str = SCOPE_LETTERS_NUMBERS):
        self.scope = scope
        self.map: dict[str, str] = {k: k for k in self.active_keys}

    @property
    def active_keys(self) -> list[str]:
        return _SCOPE_KEYS[self.scope]

    def set_scope(self, scope: str) -> None:
        self.scope = scope
        self.map = {k: k for k in self.active_keys}

    def randomize(self, secret: str = "") -> None:
        keys = self.active_keys
        values = keys.copy()
        if secret:
            seed = int.from_bytes(hashlib.sha256(secret.encode()).digest(), 'big')
            random.Random(seed).shuffle(values)
        else:
            random.SystemRandom().shuffle(values)
        self.map = dict(zip(keys, values))

    def reset(self) -> None:
        self.map = {k: k for k in self.active_keys}

    def get(self, physical_key: str) -> str:
        return self.map.get(physical_key.upper(), physical_key)
