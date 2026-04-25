"""seneca.jpg → 투명 PNG + favicon 세트.

원본 1024×1024 RGB JPG (검은 원 안의 세네카 일러스트)에서:
1. 원형 마스크로 검은 원 테두리 제거 (마스크 외부는 알파 0)
2. 흰 배경 제거 (마스크 내부에서 R,G,B ≥ 245인 픽셀의 알파 0)
3. 알파 > 0 픽셀의 bounding box 검출 → 패딩 후 크롭
4. logo.png 저장
5. 정사각 패딩 후 LANCZOS 다운스케일하여 favicon 4종 생성
6. ICO는 16/32/48 멀티 해상도

run: python assets/build_logo.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "seneca.jpg"
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)


def main() -> None:
    src = Image.open(SRC).convert("RGBA")
    w, h = src.size
    print(f"source: {w}×{h}")

    # 1. circular mask — clear pixels outside radius 478 from center
    cx, cy = w // 2, h // 2
    radius = 478
    px = src.load()
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            if dx * dx + dy * dy > radius * radius:
                px[x, y] = (0, 0, 0, 0)
                continue
            r, g, b, _ = px[x, y]
            # 2. white background → transparent
            if r >= 245 and g >= 245 and b >= 245:
                px[x, y] = (r, g, b, 0)

    # 3. crop to bbox
    bbox = src.getbbox()
    print(f"bbox after crop: {bbox}")
    cropped = src.crop(bbox).copy()
    # add small padding
    pad = 8
    pw, ph = cropped.size
    padded = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0))
    padded.paste(cropped, (pad, pad), cropped)
    print(f"logo size: {padded.size}")

    logo_path = OUT / "logo.png"
    padded.save(logo_path, "PNG", optimize=True)
    print(f"wrote {logo_path}")

    # 4. favicons — square pad to a 1:1 canvas first
    sq_side = max(padded.size)
    sq = Image.new("RGBA", (sq_side, sq_side), (0, 0, 0, 0))
    sq.paste(padded, ((sq_side - padded.size[0]) // 2, (sq_side - padded.size[1]) // 2), padded)

    fav32 = sq.resize((32, 32), Image.LANCZOS)
    fav32.save(OUT / "favicon-32.png", "PNG", optimize=True)
    print(f"wrote {OUT / 'favicon-32.png'}")

    fav180 = sq.resize((180, 180), Image.LANCZOS)
    fav180.save(OUT / "favicon-180.png", "PNG", optimize=True)
    print(f"wrote {OUT / 'favicon-180.png'}")

    # 5. ICO — multi-resolution
    ico_path = OUT / "favicon.ico"
    fav32.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"wrote {ico_path}")


if __name__ == "__main__":
    main()
