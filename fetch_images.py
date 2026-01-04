"""Fetch plant images from Wikipedia. Run: uv run python fetch_images.py"""
import re
import time
from pathlib import Path
import requests

CACHE_DIR = Path(__file__).parent / "cache" / "images"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def safe_name(latin: str) -> str:
    return re.sub(r"[^\w\s-]", "", latin).replace(" ", "_").lower()


def get_wikipedia_images(search_term: str, limit: int = 10) -> list[str]:
    """Get image URLs from Wikipedia page."""
    # First, search for the page
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_term,
        "srlimit": 1,
        "format": "json",
    }
    try:
        resp = requests.get(search_url, params=params, timeout=10)
        data = resp.json()
        results = data.get("query", {}).get("search", [])
        if not results:
            return []
        title = results[0]["title"]
    except Exception as e:
        print(f"  Search failed: {e}")
        return []

    # Get images from the page
    params = {
        "action": "query",
        "titles": title,
        "prop": "images",
        "imlimit": limit,
        "format": "json",
    }
    try:
        resp = requests.get(search_url, params=params, timeout=10)
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        image_titles = []
        for page in pages.values():
            for img in page.get("images", []):
                t = img["title"]
                # Filter out icons, logos, etc.
                if any(skip in t.lower() for skip in ["icon", "logo", "flag", "map", "commons", "wikidata"]):
                    continue
                if any(ext in t.lower() for ext in [".jpg", ".jpeg", ".png"]):
                    image_titles.append(t)
        return get_image_urls(image_titles[:limit])
    except Exception as e:
        print(f"  Image list failed: {e}")
        return []


def get_image_urls(titles: list[str]) -> list[str]:
    """Convert image titles to actual URLs."""
    if not titles:
        return []
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        urls = []
        for page in data.get("query", {}).get("pages", {}).values():
            info = page.get("imageinfo", [{}])[0]
            if "url" in info:
                urls.append(info["url"])
        return urls
    except Exception:
        return []


def download_image(url: str, path: Path) -> bool:
    """Download image to path."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "PlantQuiz/1.0"})
        if resp.status_code == 200 and len(resp.content) > 5000:  # Skip tiny images
            path.write_bytes(resp.content)
            return True
    except Exception:
        pass
    return False


def fetch_for_plant(latin: str, count: int = 5) -> int:
    """Fetch images for a plant. Returns number downloaded."""
    name = safe_name(latin)
    existing = list(CACHE_DIR.glob(f"{name}_*.jpg"))
    if len(existing) >= count:
        return len(existing)

    print(f"Fetching: {latin}")

    # Try different search terms
    search_terms = [
        latin.split("'")[0].strip(),  # Without cultivar
        latin,
        f"{latin} tree",
        f"{latin} plant",
    ]

    all_urls = []
    for term in search_terms:
        urls = get_wikipedia_images(term, limit=10)
        all_urls.extend(urls)
        if len(set(all_urls)) >= count * 2:
            break
        time.sleep(0.5)

    # Remove duplicates, keep order
    seen = set()
    unique_urls = [u for u in all_urls if not (u in seen or seen.add(u))]

    downloaded = len(existing)
    for i, url in enumerate(unique_urls):
        if downloaded >= count:
            break
        path = CACHE_DIR / f"{name}_{downloaded + 1}.jpg"
        if download_image(url, path):
            print(f"  Downloaded {downloaded + 1}/{count}")
            downloaded += 1
        time.sleep(0.3)

    return downloaded


if __name__ == "__main__":
    import csv

    plants_csv = Path(__file__).parent / "data" / "plants.csv"
    with open(plants_csv, newline="", encoding="utf-8") as f:
        plants = [row["latin"] for row in csv.DictReader(f)]

    print(f"Fetching images for {len(plants)} plants...\n")

    total = 0
    for plant in plants:
        n = fetch_for_plant(plant, count=5)
        total += n
        print(f"  → {n} images\n")
        time.sleep(1)

    print(f"\nDone! Total images: {total}")
