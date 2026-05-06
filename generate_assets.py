"""Generate Store icon assets for Account Prospecting Agent."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'packaging', 'Assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

# Purple/blue gradient-style icon with crosshair/target design
BG_COLOR = (91, 76, 255)  # #5b4cff
FG_COLOR = (255, 255, 255)

SIZES = {
    'Square44x44Logo.png': 44,
    'Square44x44Logo.scale-200.png': 88,
    'Square150x150Logo.png': 150,
    'Square150x150Logo.scale-200.png': 300,
    'Square310x310Logo.png': 310,
    'Wide310x150Logo.png': (310, 150),
    'Wide310x150Logo.scale-200.png': (620, 300),
    'SplashScreen.png': (620, 300),
    'StoreLogo.png': 50,
    'StoreLogo.scale-200.png': 100,
}


def draw_icon(img, size):
    """Draw crosshair/target icon."""
    draw = ImageDraw.Draw(img)
    if isinstance(size, tuple):
        w, h = size
    else:
        w = h = size

    cx, cy = w // 2, h // 2
    r = min(w, h) // 3

    # Outer circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=FG_COLOR, width=max(2, r // 12))
    # Inner circle
    r2 = r * 2 // 3
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=FG_COLOR, width=max(2, r // 14))
    # Center dot
    r3 = max(3, r // 5)
    draw.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=FG_COLOR)
    # Crosshairs
    lw = max(2, r // 14)
    gap = r3 + 2
    draw.line([cx, cy - r - r // 4, cx, cy - gap], fill=FG_COLOR, width=lw)
    draw.line([cx, cy + gap, cx, cy + r + r // 4], fill=FG_COLOR, width=lw)
    draw.line([cx - r - r // 4, cy, cx - gap, cy], fill=FG_COLOR, width=lw)
    draw.line([cx + gap, cy, cx + r + r // 4, cy], fill=FG_COLOR, width=lw)


for name, size in SIZES.items():
    if isinstance(size, tuple):
        img = Image.new('RGB', size, BG_COLOR)
    else:
        img = Image.new('RGB', (size, size), BG_COLOR)
    draw_icon(img, size)
    img.save(os.path.join(ASSETS_DIR, name))
    print(f"  ✓ {name}")

print(f"\nAll assets saved to {ASSETS_DIR}")
