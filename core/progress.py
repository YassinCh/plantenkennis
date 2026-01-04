import json
from datetime import date
from pathlib import Path


class Progress:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._progress_file = cache_dir / "progress.json"
        self._mistakes_file = cache_dir / "mistakes.json"

    def _load_json(self, path: Path, default: dict | list) -> dict | list:
        if path.exists():
            return json.loads(path.read_text())
        return default

    def _save_json(self, path: Path, data: dict | list):
        path.write_text(json.dumps(data, indent=2))

    # Progress tracking
    def get_progress(self) -> dict:
        return self._load_json(self._progress_file, {"sessions": [], "high_score": 0})

    def save_session(self, score: int, max_score: int, grade: float):
        progress = self.get_progress()
        progress["sessions"].append({
            "date": str(date.today()),
            "score": score,
            "max_score": max_score,
            "grade": grade,
        })
        if score > progress["high_score"]:
            progress["high_score"] = score
        self._save_json(self._progress_file, progress)

    # Mistakes tracking
    def get_mistakes(self) -> list[str]:
        return self._load_json(self._mistakes_file, [])

    def add_mistake(self, latin: str):
        mistakes = self.get_mistakes()
        if latin not in mistakes:
            mistakes.append(latin)
            self._save_json(self._mistakes_file, mistakes)

    def remove_mistake(self, latin: str):
        mistakes = self.get_mistakes()
        if latin in mistakes:
            mistakes.remove(latin)
            self._save_json(self._mistakes_file, mistakes)
