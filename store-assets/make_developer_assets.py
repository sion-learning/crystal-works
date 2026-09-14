"""Google Play デベロッパーページ用の画像素材を生成する。

生成物（このスクリプトと同じディレクトリに出力）:
  - developer-icon-512.png        512x512      デベロッパーのアイコン
  - developer-header-4096x2304.png 4096x2304   デベロッパーページのヘッダー画像

Google Playの要件: JPEGまたは24ビットPNG（非透過）・各1MB以下。

配色はEorzea Landmarksアプリのテーマ（lib/theme/app_colors.dart）に合わせ、
S-44で作成したフィーチャーグラフィックと同じ視覚言語（暗い背景・円のモチーフ・
textPrimaryの見出し・accentのサブテキスト）に揃えている。
ブランド単位の素材のため、FF14に由来する意匠は使わない。

使い方: python3 make_developer_assets.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = Path(__file__).resolve().parent

BG_PRIMARY = (0x0F, 0x11, 0x17)
BG_SECONDARY = (0x16, 0x19, 0x20)
BG_TERTIARY = (0x1E, 0x21, 0x28)
TEXT_PRIMARY = (0xD0, 0xD4, 0xE0)
ACCENT = (0x4A, 0xB4, 0xFF)

FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD_INDEX = 1  # Helvetica.ttc の Bold フェイス

WORDMARK = "Crystal Works"
TAGLINE = "Fan-made companion apps for MMO players"


def build_header(width=4096, height=2304):
    # トリミングされても構図が崩れないよう、要素はすべて中央に寄せる
    glow = Image.new("RGB", (width, height), BG_PRIMARY)
    gd = ImageDraw.Draw(glow)
    r = int(height * 0.85)
    gd.ellipse(
        [width // 2 - r, height // 2 - r, width // 2 + r, height // 2 + r],
        fill=BG_SECONDARY,
    )
    r2 = int(height * 0.52)
    gd.ellipse(
        [width // 2 - r2, height // 2 - r2, width // 2 + r2, height // 2 + r2],
        fill=BG_TERTIARY,
    )
    base = glow.filter(ImageFilter.GaussianBlur(220))

    # 装飾：アクセント色の菱形を四隅付近に薄く散らす
    deco = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    for cx, cy, size, alpha in [
        (560, 470, 190, 40),
        (3560, 1830, 230, 34),
        (3720, 430, 120, 28),
        (430, 1900, 140, 26),
    ]:
        dd.polygon(
            [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)],
            outline=ACCENT + (alpha,),
            width=8,
        )
    base = Image.alpha_composite(base.convert("RGBA"), deco).convert("RGB")

    draw = ImageDraw.Draw(base)

    sym_cy = height // 2 - 300
    draw.polygon(
        [
            (width // 2, sym_cy - 150),
            (width // 2 + 130, sym_cy),
            (width // 2, sym_cy + 150),
            (width // 2 - 130, sym_cy),
        ],
        outline=ACCENT,
        width=14,
    )

    title_font = ImageFont.truetype(FONT_PATH, 300, index=FONT_BOLD_INDEX)
    sub_font = ImageFont.truetype(FONT_PATH, 108, index=0)

    def draw_centered(text, font, y, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (width - (bbox[2] - bbox[0])) / 2 - bbox[0]
        draw.text((x, y), text, font=font, fill=fill)

    draw_centered(WORDMARK, title_font, height // 2 - 40, TEXT_PRIMARY)
    draw_centered(TAGLINE, sub_font, height // 2 + 400, ACCENT)
    return base


def build_icon(size=512):
    # ヘッダーと同じ菱形モチーフ。アプリ個別のアイコンではなくブランドの記号にすることで、
    # 今後アプリが増えても意味が破綻しないようにしている
    glow = Image.new("RGB", (size, size), BG_PRIMARY)
    gd = ImageDraw.Draw(glow)
    r = int(size * 0.36)
    gd.ellipse(
        [size // 2 - r, size // 2 - r, size // 2 + r, size // 2 + r], fill=BG_TERTIARY
    )
    base = glow.filter(ImageFilter.GaussianBlur(46))

    draw = ImageDraw.Draw(base)
    for half, filled in ((168, False), (74, True)):
        points = [
            (size // 2, size // 2 - half),
            (size // 2 + half, size // 2),
            (size // 2, size // 2 + half),
            (size // 2 - half, size // 2),
        ]
        if filled:
            draw.polygon(points, fill=ACCENT)
        else:
            draw.polygon(points, outline=ACCENT, width=18)
    return base


def main():
    targets = [
        (build_icon(), OUT_DIR / "developer-icon-512.png"),
        (build_header(), OUT_DIR / "developer-header-4096x2304.png"),
    ]
    for image, path in targets:
        image.save(path, "PNG", optimize=True)
        size_kb = path.stat().st_size / 1024
        assert image.mode == "RGB", f"{path.name}: 非透過(RGB)である必要がある"
        assert size_kb < 1024, f"{path.name}: 1MBを超えている ({size_kb:.0f}KB)"
        print(f"{path.name}: {image.width}x{image.height} {size_kb:.0f}KB")


if __name__ == "__main__":
    main()
