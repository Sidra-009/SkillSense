import os
from typing import List

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def top_n_skills(skills: List[dict], n: int = 10) -> List[dict]:
    return sorted(skills, key=lambda s: s.get("confidence",0), reverse=True)[:n]
