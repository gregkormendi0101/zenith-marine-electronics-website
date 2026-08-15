from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).parent
SOURCE_DIR = ROOT.parent / "zenith-v3-image-sources"
OUT = ROOT / "assets" / "images"

SOURCES = {
    "working-helm.jpg": "https://unsplash.com/photos/cIdcOJaWuy0/download?force=true&w=2800",
    "navigation-display.jpg": "https://unsplash.com/photos/SacHhp1_6_U/download?force=true&w=2400",
    "radio-console.jpg": "https://unsplash.com/photos/rBw2BQLCHdo/download?force=true&w=2400",
}


def download_sources() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in SOURCES.items():
        destination = SOURCE_DIR / filename
        if destination.exists():
            continue
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=90) as response:
            destination.write_bytes(response.read())
        print(f"downloaded {filename}")


def save_cover(
    source: str,
    target: str,
    size: tuple[int, int],
    centering: tuple[float, float] = (0.5, 0.5),
    quality: int = 84,
) -> None:
    with Image.open(SOURCE_DIR / source) as image:
        image = image.convert("RGB")
        fitted = ImageOps.fit(
            image,
            size,
            method=Image.Resampling.LANCZOS,
            centering=centering,
        )
        fitted.save(OUT / target, "WEBP", quality=quality, method=6)


def main() -> None:
    download_sources()
    OUT.mkdir(parents=True, exist_ok=True)

    save_cover("working-helm.jpg", "hero-2400.webp", (2400, 1500), (0.54, 0.5), 86)
    save_cover("working-helm.jpg", "hero-1440.webp", (1440, 900), (0.54, 0.5), 84)
    save_cover("working-helm.jpg", "hero-mobile-1200.webp", (1200, 1600), (0.58, 0.5), 86)
    save_cover("working-helm.jpg", "hero-mobile-750.webp", (750, 1000), (0.58, 0.5), 83)

    save_cover("navigation-display.jpg", "navigation-display-1400.webp", (1400, 1750), (0.5, 0.48), 85)
    save_cover("navigation-display.jpg", "navigation-display-800.webp", (800, 1000), (0.5, 0.48), 82)

    save_cover("radio-console.jpg", "radio-console-1600.webp", (1600, 1200), (0.47, 0.46), 84)
    save_cover("radio-console.jpg", "radio-console-900.webp", (900, 675), (0.47, 0.46), 82)

    save_cover("working-helm.jpg", "social.webp", (1200, 630), (0.52, 0.5), 85)

    for path in sorted(OUT.glob("*.webp")):
        with Image.open(path) as image:
            print(
                f"{path.name}: {image.width}x{image.height} — "
                f"{path.stat().st_size / 1024:.0f} KB"
            )


if __name__ == "__main__":
    main()
