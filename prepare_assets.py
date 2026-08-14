from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
SRC = ROOT.parent / "zenith-v2-image-sources"
OUT = ROOT / "assets" / "images"


def save_fit(source: str, target: str, size: tuple[int, int], quality: int = 84, centering: tuple[float, float] = (0.5, 0.5)) -> None:
    with Image.open(SRC / source) as image:
        image = image.convert("RGB")
        fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=centering)
        fitted.save(OUT / target, "WEBP", quality=quality, method=6)


for source, stem in (("hero.png", "hero"), ("helm.png", "helm"), ("dock.png", "dock")):
    save_fit(source, f"{stem}-2560.webp", (2560, 1280), 84)
    save_fit(source, f"{stem}-1440.webp", (1440, 720), 82)

save_fit("hero-mobile.png", "hero-mobile-1440.webp", (1440, 2560), 84, (0.5, 0.5))
save_fit("hero-mobile.png", "hero-mobile-900.webp", (900, 1600), 82, (0.5, 0.5))
save_fit("hero.png", "social.webp", (1200, 630), 84, (0.58, 0.5))

for path in sorted(OUT.glob("*.webp")):
    with Image.open(path) as image:
        print(f"{path.name}: {image.width}x{image.height} — {path.stat().st_size / 1024:.0f} KB")
