import json
from fastapi import HTTPException
from pathlib import Path
from typing import Any
from Services.LogServices import AddLogOrError

resources_path = Path(__file__).resolve().parent.parent.parent / "Resources" / "Resources.json"

def LoadJsonFromFile(key: str) -> Any:
    try:
        with open(resources_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        value = data.get(key)
        if value is None:  # to catch keys with falsy values like empty string or 0
            raise KeyError(f"'{key}' not found in Resources.json")
        return value
    except Exception as ex:
        AddLogOrError(f"Error loading key '{key}' from JSON: {ex}", "ERROR")
        raise HTTPException(ex)
    

