import re
import random
from pathlib import Path


def _safe_folder(latin: str) -> str:
    """Convert latin name to folder name (lowercase, underscores, no special chars)."""
    name = latin
    # Remove cultivar names in quotes (everything after first quote)
    name = re.sub(r"\s*['\u2019].*$", "", name)
    # Remove "cultivars" suffix
    name = re.sub(r"\s+cultivars?\b", "", name, flags=re.IGNORECASE)
    # Handle hybrids like "Tilia x europaea"
    name = re.sub(r"\s+x\s+", "_x_", name)
    # Remove remaining special chars
    name = re.sub(r"[^\w\s-]", "", name)
    return name.replace(" ", "_").lower().strip("_")


def get_random_image(latin: str, images_dir: Path) -> Path | None:
    """Get a random image from the plant's folder."""
    folder_name = _safe_folder(latin)
    plant_folder = images_dir / folder_name

    if not plant_folder.exists():
        return None

    # Get all image files (jpg, jpeg, png)
    images = list(plant_folder.glob("*.jpg")) + list(plant_folder.glob("*.jpeg")) + list(plant_folder.glob("*.png"))

    return random.choice(images) if images else None
