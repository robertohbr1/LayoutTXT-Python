"""Persistência de preferências (substitui GetSetting/SaveSetting do registro)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass
class AppSettings:
    """Últimos arquivos usados e geometria da janela."""

    layout_path: str = ""
    data_path: str = ""
    geometry: str = ""
    zoomed: bool = False


def default_settings_path() -> Path:
    """`%APPDATA%/LayoutTXT/settings.json` (ou `~/.layouttxt/settings.json`)."""
    base = os.environ.get("APPDATA")
    return Path(base) / "LayoutTXT" / "settings.json" if base else Path.home() / ".layouttxt" / "settings.json"


class JsonSettingsStore:
    """Lê e grava `AppSettings` num arquivo JSON.

    Exemplo:
        >>> store = JsonSettingsStore(Path("settings.json"))  # doctest: +SKIP
        >>> store.save(AppSettings(layout_path="CCS.csv"))      # doctest: +SKIP
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> AppSettings:
        """Preferências salvas; padrão se o arquivo não existir ou for inválido."""
        try:
            stored = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return AppSettings()
        known = {field.name for field in fields(AppSettings)}
        return AppSettings(**{key: value for key, value in stored.items() if key in known})

    def save(self, settings: AppSettings) -> None:
        """Grava as preferências, criando a pasta se necessário."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")
