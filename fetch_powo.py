"""Fetch all images from POWO for each plant."""
import csv
import re
import time
from pathlib import Path
import requests

BASE = Path(__file__).parent
POWO_DIR = BASE / "cache" / "images_powo"

# POWO taxon IDs for each plant (searched manually)
POWO_IDS = {
    "Acer campestre": "781250-1",
    "Acer platanoides": "781455-1",
    "Acer pseudoplatanus": "781462-1",
    "Aesculus hippocastanum": "781594-1",
    "Alnus cordata": "294902-1",
    "Alnus glutinosa": "295056-2",
    "Betula pendula": "295315-2",
    "Carpinus betulus": "295563-2",
    "Castanea sativa": "841733-1",
    "Crataegus laevigata": "723164-1",
    "Fagus sylvatica": "295766-2",
    "Fraxinus excelsior": "610675-1",
    "Gleditsia triacanthos": "508998-1",
    "Juglans regia": "295941-2",
    "Liquidambar styraciflua": "36667-1",
    "Magnolia grandiflora": "554301-1",
    "Magnolia kobus": "554448-1",
    "Malus": "30008581-2",  # genus
    "Platanus": "30017203-2",  # genus - hispanica is hybrid
    "Populus alba": "296587-2",
    "Populus": "30018303-2",  # genus for canadensis
    "Prunus spinosa": "729468-1",
    "Prunus": "30019502-2",  # genus for subhirtella
    "Pyrus calleryana": "729909-1",
    "Quercus palustris": "296960-2",
    "Quercus robur": "296977-2",
    "Robinia pseudoacacia": "509766-1",
    "Salix": "30021712-2",  # genus for sepulcralis
    "Sorbus aucuparia": "719533-1",
    "Tilia cordata": "633855-1",
    "Tilia": "30023006-2",  # genus for europaea
    "Ulmus": "30023411-2",  # genus for hollandica
    "Acer palmatum": "781412-1",
    "Berberis thunbergii": "94308-1",
    "Buddleja davidii": "113998-1",
    "Chaenomeles japonica": "721859-1",
    "Cornus alba": "745002-1",
    "Corylus avellana": "295652-2",
    "Cotinus coggygria": "19818-1",
    "Forsythia": "610383-2",  # genus for intermedia
    "Hibiscus syriacus": "558082-1",
    "Hippophae rhamnoides": "402016-1",
    "Hydrangea arborescens": "840137-1",
    "Hydrangea macrophylla": "840236-1",
    "Hypericum": "30013096-2",  # genus
    "Ligustrum vulgare": "611256-1",
    "Magnolia": "30015233-2",  # genus for soulangeana
    "Philadelphus coronarius": "840750-1",
}


def safe_folder(name: str) -> str:
    """Convert plant name to folder name."""
    return re.sub(r"[^\w\s-]", "", name).replace(" ", "_").lower()


HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def fetch_powo_images(taxon_id: str) -> list[str]:
    """Fetch image URLs from POWO page."""
    # Try both URL formats
    urls_to_try = [
        f"https://powo.science.kew.org/taxon/{taxon_id}",
        f"https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:{taxon_id}",
    ]

    for url in urls_to_try:
        try:
            resp = requests.get(url, timeout=30, allow_redirects=True, headers=HEADERS)
            if resp.status_code != 200:
                continue
            # Extract cloudfront URLs
            pattern = r'd2seqvvyy3b8p2\.cloudfront\.net/([a-f0-9]+)\.jpg'
            matches = re.findall(pattern, resp.text)
            if matches:
                return list(set(matches))  # unique
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
    return []


def download_images(plant_name: str, image_ids: list[str]):
    """Download images to plant folder."""
    folder = POWO_DIR / safe_folder(plant_name)
    folder.mkdir(parents=True, exist_ok=True)

    for i, img_id in enumerate(image_ids, 1):
        path = folder / f"{i:02d}.jpg"
        if path.exists():
            continue
        try:
            url = f"https://d2seqvvyy3b8p2.cloudfront.net/{img_id}.jpg"
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                path.write_bytes(resp.content)
        except Exception:
            pass
        time.sleep(0.2)


def main():
    for plant, taxon_id in POWO_IDS.items():
        folder = POWO_DIR / safe_folder(plant)
        existing = list(folder.glob("*.jpg")) if folder.exists() else []
        if len(existing) >= 5:
            print(f"Skipping {plant} (already have {len(existing)} images)")
            continue

        print(f"Fetching {plant}...")
        image_ids = fetch_powo_images(taxon_id)
        print(f"  Found {len(image_ids)} images")
        download_images(plant, image_ids)
        time.sleep(1)


if __name__ == "__main__":
    main()
