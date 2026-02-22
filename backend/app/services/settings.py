from __future__ import annotations

import json
from pathlib import Path

try:
    import keyring
except ImportError:  # pragma: no cover
    keyring = None


class SettingsStore:
    SERVICE_NAME = "qwenworkbench"
    TOKEN_KEY = "hf_token"

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "qwenworkbench"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / "settings.json"
        if not self.settings_file.exists():
            self._write(
                {
                    "model_cache_dir": str(
                        Path.home() / "Library/Application Support/QwenWorkbench/models"
                    ),
                    "reserve_gb": 10,
                    "token_storage": "unset",
                }
            )

    def _read(self) -> dict:
        return json.loads(self.settings_file.read_text(encoding="utf-8"))

    def _write(self, payload: dict) -> None:
        self.settings_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self) -> dict:
        return self._read()

    def patch(self, **kwargs) -> dict:
        current = self._read()
        for key, value in kwargs.items():
            if value is not None:
                current[key] = value
        self._write(current)
        return current

    def save_token(self, token: str) -> dict:
        if keyring:
            try:
                keyring.set_password(self.SERVICE_NAME, self.TOKEN_KEY, token)
                data = self.patch(token_storage="keyring")
                return {"ok": True, "storage": "keyring", "settings": data}
            except Exception:
                pass

        data = self.patch(hf_token=token, token_storage="config_warning")
        return {"ok": True, "storage": "config_warning", "settings": data}

    def get_token(self) -> str | None:
        if keyring:
            try:
                token = keyring.get_password(self.SERVICE_NAME, self.TOKEN_KEY)
                if token:
                    return token
            except Exception:
                pass
        return self._read().get("hf_token")
