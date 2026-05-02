#!/usr/bin/env python3
"""
団体リスト用 プレースホルダー画像生成スクリプト
サイズ: 1280x720 (16:9)
デザイン: カテゴリカラー帯 + ロゴ + 団体名 + 地域
"""

import os
import sys
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---- 設定 ----
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../public/placeholders')
LOGO_PATH  = os.path.join(os.path.dirname(__file__), '../public/logo.png')
W, H = 1280, 720

FONT_BOLD  = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
FONT_REG   = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'

# カテゴリ → (背景グラデーション開始色, 終了色)
CATEGORY_COLORS: dict[str, tuple[tuple, tuple]] = {
    '観光交流': ((254, 243, 199), (253, 230, 138)),  # amber-100 → amber-200
    '産業':    ((219, 234, 254), (191, 219, 254)),   # blue-100 → blue-200
    '農林業':  ((220, 252, 231), (187, 247, 208)),   # green-100 → green-200
    '環境':    ((204, 251, 241), (153, 246, 228)),   # teal-100 → teal-200
    '福祉健康':((243, 232, 255), (233, 213, 255)),   # purple-100 → purple-200
    '教育':    ((224, 231, 255), (199, 210, 254)),   # indigo-100 → indigo-200
    '文化':    ((252, 231, 243), (251, 207, 232)),   # pink-100 → pink-200
    '移住':    ((209, 250, 229), (167, 243, 208)),   # emerald-100 → emerald-200
    '防災':    ((254, 226, 226), (254, 202, 202)),   # red-100 → red-200
    '情報発信':((207, 250, 254), (165, 243, 252)),   # cyan-100 → cyan-200
}
DEFAULT_COLORS = ((243, 244, 246), (229, 231, 235))  # gray-100 → gray-200

TEXT_DARK  = (30, 30, 30)
TEXT_MID   = (80, 80, 80)
ACCENT_RED = (220, 38, 38)   # red-600

os.makedirs(OUTPUT_DIR, exist_ok=True)

def make_gradient(w: int, h: int, c1: tuple, c2: tuple) -> Image.Image:
    """左上→右下のグラデーション背景"""
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img

def fit_text(draw, text: str, font_path: str, max_width: int, size_start: int = 72) -> ImageFont.FreeTypeFont:
    """最大幅に収まるフォントサイズを返す"""
    size = size_start
    while size > 18:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, 18)

def generate(org: dict) -> str:
    name      = org['name']
    area_raw  = org.get('area') or ''
    area      = '・'.join(area_raw) if isinstance(area_raw, list) else (area_raw or '')
    categories = org.get('category', [])
    org_id    = org['id']

    # カテゴリ → 背景色決定（最初のカテゴリを使用）
    first_cat = categories[0] if categories else ''
    c1, c2 = CATEGORY_COLORS.get(first_cat, DEFAULT_COLORS)

    # --- 背景 ---
    img = make_gradient(W, H, c1, c2)
    draw = ImageDraw.Draw(img)

    # --- ロゴ（右下・半透明） ---
    logo_orig = Image.open(LOGO_PATH).convert('RGBA')
    logo_h = 200
    logo_w = int(logo_orig.width * logo_h / logo_orig.height)
    logo = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)

    # 半透明化
    r, g, b, a = logo.split()
    a = a.point(lambda x: int(x * 0.12))
    logo.putalpha(a)

    logo_x = W - logo_w - 40
    logo_y = H - logo_h - 30
    img.paste(logo, (logo_x, logo_y), logo)

    # --- 左上アクセントライン ---
    draw.rectangle([(0, 0), (8, H)], fill=ACCENT_RED)

    # --- カテゴリタグ ---
    tag_font = ImageFont.truetype(FONT_REG, 22)
    tag_x = 48
    tag_y = 60
    for cat in categories[:3]:
        bbox = draw.textbbox((0, 0), cat, font=tag_font)
        tw = bbox[2] - bbox[0]
        pad_x, pad_y = 14, 6
        draw.rounded_rectangle(
            [(tag_x - pad_x, tag_y - pad_y), (tag_x + tw + pad_x, tag_y + (bbox[3]-bbox[1]) + pad_y)],
            radius=20, fill=ACCENT_RED
        )
        draw.text((tag_x, tag_y), cat, font=tag_font, fill=(255, 255, 255))
        tag_x += tw + pad_x * 2 + 10

    # --- 団体名（中央） ---
    name_font = fit_text(draw, name, FONT_BOLD, W - 100, size_start=80)
    name_bbox = draw.textbbox((0, 0), name, font=name_font)
    nw = name_bbox[2] - name_bbox[0]
    nh = name_bbox[3] - name_bbox[1]
    nx = (W - nw) // 2
    ny = (H - nh) // 2 - 20

    # テキストシャドウ
    draw.text((nx + 2, ny + 2), name, font=name_font, fill=(0, 0, 0, 40))
    draw.text((nx, ny), name, font=name_font, fill=TEXT_DARK)

    # --- 地域 ---
    area_font = ImageFont.truetype(FONT_REG, 28)
    area_bbox = draw.textbbox((0, 0), area, font=area_font)
    aw = area_bbox[2] - area_bbox[0]
    ax = (W - aw) // 2
    ay = ny + nh + 18
    draw.text((ax, ay), area, font=area_font, fill=TEXT_MID)

    # --- サイト名（右下） ---
    site_font = ImageFont.truetype(FONT_REG, 18)
    site_text = '火の国未来創造ネット'
    site_bbox = draw.textbbox((0, 0), site_text, font=site_font)
    sw = site_bbox[2] - site_bbox[0]
    draw.text((W - sw - 20, H - 36), site_text, font=site_font, fill=TEXT_MID)

    # --- 保存 ---
    out_path = os.path.join(OUTPUT_DIR, f'{org_id}.jpg')
    img.convert('RGB').save(out_path, 'JPEG', quality=90)
    print(f'  生成: {name} → {out_path}')
    return out_path


if __name__ == '__main__':
    # microCMS からデータ取得
    import urllib.request, json
    API_KEY    = os.environ.get('MICROCMS_API_KEY', 'bnexp8nRPHd4dhUOxlLMD3VqybEe9MQzfZo4')
    DOMAIN     = os.environ.get('MICROCMS_SERVICE_DOMAIN', 'hinokuni-mirai')
    url = f'https://{DOMAIN}.microcms.io/api/v1/organizations?limit=100'
    req = urllib.request.Request(url, headers={'X-MICROCMS-API-KEY': API_KEY})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())

    orgs = data['contents']
    print(f'{len(orgs)} 件の団体を処理します\n')
    for org in orgs:
        generate(org)
    print('\n完了！')
