from typing import Dict, Optional

_appSettingsCache: Dict[str, str] = {}

def Set(settings: Dict[str, str]) -> None:
    _appSettingsCache.clear()
    _appSettingsCache.update({k.upper(): v for k, v in settings.items()})

def Get(key: str) -> Optional[str]:
    return _appSettingsCache.get(key.upper())
