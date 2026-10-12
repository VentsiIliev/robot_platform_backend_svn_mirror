#!/usr/bin/env python3
"""Resize the existing PL PROJECT artwork into native mobile assets.

Run from any directory: python3 res/generate_mobile_branding.py
Requires Pillow. Does not generate or alter the source artwork.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
icon = Image.open(ROOT / "flutter/assets/pl_project_app_icon.png").convert("RGBA")
logo = Image.open(ROOT / "flutter/assets/pl_project_logo.png").convert("RGBA")
android = ROOT / "flutter/android/app/src/main/res"
ios = ROOT / "flutter/ios/Runner/Assets.xcassets"


def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def resize(image, size):
    return image.resize(size, Image.Resampling.LANCZOS)


for density, scale in [("mdpi", 1), ("hdpi", 1.5), ("xhdpi", 2),
                       ("xxhdpi", 3), ("xxxhdpi", 4)]:
    folder = android / f"mipmap-{density}"
    size = round(48 * scale)
    launcher = Image.new("RGBA", (size, size), "white")
    launcher.alpha_composite(resize(icon, (size, size)))
    save(launcher.convert("RGB"), folder / "ic_launcher.png")
    size = round(108 * scale)
    foreground = Image.new("RGBA", (size, size))
    artwork_size = round(66 * scale)
    inset = (size - artwork_size) // 2
    foreground.alpha_composite(resize(icon, (artwork_size, artwork_size)), (inset, inset))
    save(foreground, folder / "ic_launcher_foreground.png")
    # Android notification icons use a white silhouette on transparency.
    size = round(24 * scale)
    notification = Image.new("RGBA", (size, size), "white")
    notification.putalpha(resize(icon, (size, size)).getchannel("A"))
    save(notification, folder / "ic_stat_logo.png")
    save(resize(logo, (round(192 * scale), round(78 * scale))),
         android / f"drawable-{density}" / "pl_project_launch.png")

catalog = ios / "AppIcon.appiconset"
for entry in json.loads((catalog / "Contents.json").read_text())["images"]:
    size = round(float(entry["size"].split("x")[0]) * float(entry["scale"][:-1]))
    image = Image.new("RGBA", (size, size), "white")
    image.alpha_composite(resize(icon, (size, size)))
    save(image.convert("RGB"), catalog / entry["filename"])

for scale in [1, 2, 3]:
    suffix = "" if scale == 1 else f"@{scale}x"
    save(resize(logo, (192 * scale, 78 * scale)),
         ios / "LaunchImage.imageset" / f"LaunchImage{suffix}.png")

print("Generated PL PROJECT Android and iOS icons and launch images.")
