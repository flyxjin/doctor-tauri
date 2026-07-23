# -*- coding: utf-8 -*-
"""生成中药材销售管理系统桌面图标

设计理念：「悬壶本草」
- 圆角方形深绿渐变背景（与 App 主题 siderBg 一致）
- 中央白色药葫芦 — 中医药「悬壶济世」经典符号，几何简洁，小尺寸清晰
- 葫芦束腰处翠绿本草叶 — 中草药意象
- 葫芦顶部朱砂红葫芦口 — 点缀品牌色
- 底部金色弧线 — 装饰收尾

相比旧版「印章+本字」：用图形替代文字，16/32px 小尺寸下不再模糊。
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

# ==================== 配色 ====================
BG_TOP = (30, 69, 48)        # #1E4530
BG_BOTTOM = (18, 42, 30)     # #122A1E
GOURD_WHITE = (253, 250, 245)  # #FDFAF5
GOURD_HIGHLIGHT = (255, 255, 255)
LEAF_DARK = (90, 160, 70)    # #5AA046
LEAF_LIGHT = (130, 200, 90)  # #82C85A
GOLD = (205, 170, 85)        # #CDAA55
SEAL_RED = (200, 60, 45)     # #C83C2D


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def make_bg(size, radius):
    """圆角渐变背景（逐行填充，比 putpixel 快）"""
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        t = y / max(size - 1, 1)
        color = lerp_color(BG_TOP, BG_BOTTOM, t) + (255,)
        # 用 line 填充整行
        ImageDraw.Draw(grad).line([(0, y), (size, y)], fill=color)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out


def draw_leaf(draw, cx, cy, length, width, angle_deg, color, vein_color, line_w=2):
    """叶子：椭圆 + 主脉"""
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    n = 28
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = length * math.cos(t)
        y = width * math.sin(t)
        pts.append((x * cos_a - y * sin_a + cx, x * sin_a + y * cos_a + cy))
    draw.polygon(pts, fill=color)
    draw.line(
        [(-length * cos_a + cx, -length * sin_a + cy),
         (length * cos_a + cx, length * sin_a + cy)],
        fill=vein_color, width=line_w,
    )


def render_icon(size):
    """渲染指定尺寸图标（4x 超采样抗锯齿）"""
    scale = 4
    s = size * scale
    img = make_bg(s, radius=int(s * 0.18))
    draw = ImageDraw.Draw(img)
    cx = s * 0.50

    # ========== 1. 葫芦口（朱砂红小柱） ==========
    neck_w = s * 0.035
    draw.rounded_rectangle(
        [cx - neck_w, s * 0.135, cx + neck_w, s * 0.205],
        radius=max(2, int(neck_w * 0.5)), fill=SEAL_RED,
    )
    draw.ellipse(
        [cx - neck_w * 1.3, s * 0.125, cx + neck_w * 1.3, s * 0.155],
        fill=SEAL_RED,
    )

    # ========== 2. 葫芦主体（两个白色椭圆 + 束腰矩形，同色重叠自然融合） ==========
    # 上球（小）
    up_r = s * 0.135
    up_cy = s * 0.345
    draw.ellipse([cx - up_r, up_cy - up_r, cx + up_r, up_cy + up_r], fill=GOURD_WHITE)
    # 下球（大）
    dn_r = s * 0.205
    dn_cy = s * 0.625
    draw.ellipse([cx - dn_r, dn_cy - dn_r, cx + dn_r, dn_cy + dn_r], fill=GOURD_WHITE)
    # 束腰（连接两球的梯形，同色填充消除中间缝隙）
    waist_top_w = s * 0.085
    waist_bot_w = s * 0.135
    waist_top_y = up_cy + up_r * 0.5
    waist_bot_y = dn_cy - dn_r * 0.5
    draw.polygon([
        (cx - waist_top_w, waist_top_y),
        (cx + waist_top_w, waist_top_y),
        (cx + waist_bot_w, waist_bot_y),
        (cx - waist_bot_w, waist_bot_y),
    ], fill=GOURD_WHITE)

    # ========== 3. 左侧高光（模糊白椭圆，增加光泽） ==========
    hl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    hld = ImageDraw.Draw(hl)
    hld.ellipse([cx - s * 0.15, s * 0.29, cx - s * 0.04, s * 0.40], fill=(*GOURD_HIGHLIGHT, 130))
    hld.ellipse([cx - s * 0.23, s * 0.55, cx - s * 0.09, s * 0.68], fill=(*GOURD_HIGHLIGHT, 90))
    hl = hl.filter(ImageFilter.GaussianBlur(radius=s * 0.018))
    img = Image.alpha_composite(img, hl)
    draw = ImageDraw.Draw(img)

    # ========== 4. 本草叶（束腰两侧斜出） ==========
    lw = max(2, int(s * 0.008))
    draw_leaf(draw, cx - s * 0.13, s * 0.505, s * 0.10, s * 0.035, -25, LEAF_DARK, LEAF_LIGHT, lw)
    draw_leaf(draw, cx + s * 0.13, s * 0.485, s * 0.075, s * 0.028, 200, LEAF_LIGHT, LEAF_DARK, lw)

    # ========== 5. 底部金色弧线 ==========
    draw.arc(
        [int(s * 0.14), int(s * 0.80), int(s * 0.86), int(s * 1.06)],
        start=200, end=340, fill=GOLD, width=max(2, int(s * 0.014)),
    )

    # 缩小到目标尺寸
    return img.resize((size, size), Image.LANCZOS)


def write_svg(path):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1E4530"/>
      <stop offset="1" stop-color="#122A1E"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="240" height="240" rx="44" fill="url(#bg)"/>
  <rect x="123" y="30" width="10" height="20" rx="3" fill="#C83C2D"/>
  <ellipse cx="128" cy="32" rx="8" ry="5" fill="#C83C2D"/>
  <ellipse cx="128" cy="88" rx="35" ry="35" fill="#FDFAF5"/>
  <ellipse cx="128" cy="160" rx="53" ry="53" fill="#FDFAF5"/>
  <polygon points="98,104 158,104 150,132 106,132" fill="#FDFAF5"/>
  <ellipse cx="106" cy="78" rx="10" ry="7" fill="#FFFFFF" opacity="0.5"/>
  <ellipse cx="98" cy="142" rx="13" ry="9" fill="#FFFFFF" opacity="0.3"/>
  <g transform="translate(95,129) rotate(-25)">
    <ellipse cx="0" cy="0" rx="26" ry="9" fill="#5AA046"/>
    <line x1="-24" y1="0" x2="24" y2="0" stroke="#82C85A" stroke-width="2"/>
  </g>
  <g transform="translate(161,124) rotate(20)">
    <ellipse cx="0" cy="0" rx="19" ry="7" fill="#82C85A"/>
    <line x1="-17" y1="0" x2="17" y2="0" stroke="#5AA046" stroke-width="2"/>
  </g>
  <path d="M 36 215 Q 128 255 220 215" stroke="#CDAA55" stroke-width="3.5" fill="none" opacity="0.7"/>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    sizes = {"32x32.png": 32, "128x128.png": 128, "128x128@2x.png": 256}
    images = {}
    for name, sz in sizes.items():
        img = render_icon(sz)
        img.save(os.path.join(here, name))
        images[sz] = img
        print(f"  生成 {name} ({sz}x{sz})")
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images[256].save(os.path.join(here, "icon.ico"), format="ICO", sizes=ico_sizes)
    print(f"  生成 icon.ico ({os.path.getsize(os.path.join(here, 'icon.ico')) / 1024:.1f} KB)")
    write_svg(os.path.join(here, "icon.svg"))
    print("  生成 icon.svg\n图标生成完成。")


if __name__ == "__main__":
    main()
