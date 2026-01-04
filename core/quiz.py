import csv
import random
from dataclasses import dataclass
from pathlib import Path

from .matching import is_match


@dataclass
class Plant:
    latin: str
    dutch: list[str]


def load_plants(csv_path: Path) -> list[Plant]:
    """Load plants from CSV file."""
    plants = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dutch_names = [n.strip() for n in row["dutch"].split(";")]
            plants.append(Plant(latin=row["latin"], dutch=dutch_names))
    return plants


class Quiz:
    def __init__(self, plants: list[Plant]):
        self.plants = random.sample(plants, len(plants))
        self.index = 0
        self.dutch_score = 0
        self.latin_score = 0

    @property
    def current(self) -> Plant | None:
        return self.plants[self.index] if self.index < len(self.plants) else None

    @property
    def is_done(self) -> bool:
        return self.index >= len(self.plants)

    @property
    def total_score(self) -> int:
        return self.dutch_score + self.latin_score * 2

    @property
    def max_score(self) -> int:
        return len(self.plants) * 3  # 1 for dutch, 2 for latin

    def check(self, dutch_input: str, latin_input: str) -> tuple[bool, bool]:
        """Check answers, return (dutch_correct, latin_correct)."""
        plant = self.current
        if not plant:
            return False, False

        dutch_ok = is_match(dutch_input, plant.dutch)
        latin_ok = is_match(latin_input, [plant.latin])

        if dutch_ok:
            self.dutch_score += 1
        if latin_ok:
            self.latin_score += 1

        return dutch_ok, latin_ok

    def next(self):
        """Move to next plant."""
        self.index += 1

    def grade(self) -> float:
        """Calculate grade on 1-10 scale."""
        if self.max_score == 0:
            return 1.0
        return round((self.total_score / self.max_score) * 9 + 1, 1)
