# -*- coding: utf-8 -*-
"""生成中医药主题应用图标 - 研钵与本草叶"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

def create_icon(size: int) -> Image.Image:
    """生成指定尺寸的图标"""
    # 高分辨率抗锯齿：先渲染 4x 再缩小
    scale = 4
    s = size * scale
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = s / 2, s / 2
    r = s * 0.46  # 圆角矩形半径

    # === 背景：圆角方形 + 深墨绿渐变 ===
    # 手动渐变填充
    for y in range(s):
        ratio = y / s
        # 从深墨绿(30,60,50) 到 深翠绿(20,45,40)
        rr = int(30 - 10 * ratio)
        gg = int(60 - 15 * ratio)
        bb = int(50 - 10 * ratio)
        draw.line([(0, y), (s, y)], fill=(rr, gg, bb, 255))

    # 圆角遮罩
    mask = Image.new('L', (s, s), 0)
    mdraw = ImageDraw.Draw(mask)
    radius = int(r * 0.18)
    mdraw.rounded_rectangle([s*0.04, s*0.04, s*0.96, s*0.96], radius=radius, fill=255)
    img.putalpha(mask)

    # === 研钵 (mortar) ===
    # 研钵形状：上宽下窄的梯形碗
    bowl_top_w = s * 0.38
    bowl_bot_w = s * 0.26
    bowl_top_y = s * 0.52
    bowl_bot_y = s * 0.78
    bowl_cx = cx

    # 研钵主体 - 朱砂红渐变
    bowl_points = [
        (bowl_cx - bowl_top_w, bowl_top_y),
        (bowl_cx + bowl_top_w, bowl_top_y),
        (bowl_cx + bowl_bot_w, bowl_bot_y),
        (bowl_cx - bowl_bot_w, bowl_bot_y),
    ]
    # 填充研钵
    for i in range(int(bowl_bot_y - bowl_top_y)):
        ratio = i / (bowl_bot_y - bowl_top_y)
        w = bowl_top_w + (bowl_bot_w - bowl_top_w) * ratio
        y = bowl_top_y + i
        # 朱砂红渐变：上浅下深
        rr = int(200 - 30 * ratio)
        gg = int(60 - 15 * ratio)
        bb = int(45 - 10 * ratio)
        draw.line([(bowl_cx - w, y), (bowl_cx + w, y)], fill=(rr, gg, bb, 255))

    # 研钵口沿（椭圆形深色线）
    rim_h = s * 0.04
    draw.ellipse(
        [bowl_cx - bowl_top_w, bowl_top_y - rim_h/2,
         bowl_cx + bowl_top_w, bowl_top_y + rim_h/2],
        fill=(180, 50, 40, 255), outline=(120, 30, 25, 255), width=int(s*0.008)
    )

    # 研钵内壁阴影
    inner_ellipse = [
        bowl_cx - bowl_top_w * 0.88, bowl_top_y - rim_h/3,
        bowl_cx + bowl_top_w * 0.88, bowl_top_y + rim_h * 0.8
    ]
    draw.ellipse(inner_ellipse, fill=(100, 25, 20, 200))

    # === 研杵 (pestle) ===
    pestle_top_y = s * 0.14
    pestle_bot_y = s * 0.48
    pestle_top_w = s * 0.045
    pestle_bot_w = s * 0.035
    pestle_x = cx + s * 0.02  # 略偏右

    # 研杵主体 - 木色渐变
    for i in range(int(pestle_bot_y - pestle_top_y)):
        ratio = i / (pestle_bot_y - pestle_top_y)
        w = pestle_top_w + (pestle_bot_w - pestle_top_w) * ratio
        y = pestle_top_y + i
        # 木色：浅棕到深棕
        rr = int(160 - 20 * ratio)
        gg = int(110 - 15 * ratio)
        bb = int(70 - 10 * ratio)
        draw.line([(pestle_x - w, y), (pestle_x + w, y)], fill=(rr, gg, bb, 255))

    # 研杵顶部圆头
    draw.ellipse(
        [pestle_x - pestle_top_w, pestle_top_y - pestle_top_w * 0.6,
         pestle_x + pestle_top_w, pestle_top_y + pestle_top_w * 0.6],
        fill=(170, 120, 80, 255)
    )

    # === 本草叶 (herb leaves) ===
    # 左侧叶子
    leaf_color = (80, 140, 60, 255)
    leaf_highlight = (120, 180, 80, 255)

    def draw_leaf(draw, cx, cy, length, angle_deg, color, highlight):
        """绘制一片叶子"""
        angle = math.radians(angle_deg)
        # 叶子轮廓点（椭圆形）
        points = []
        leaf_w = length * 0.35
        n = 20
        for i in range(n + 1):
            t = i / n
            theta = t * 2 * math.pi
            lx = length * math.cos(theta) * 0.5
            ly = leaf_w * math.sin(theta) * 0.5
            # 旋转
            rx = lx * math.cos(angle) - ly * math.sin(angle)
            ry = lx * math.sin(angle) + ly * math.cos(angle)
            points.append((cx + rx, cy + ry))
        draw.polygon(points, fill=color)
        # 叶脉
        vein_end_x = cx + length * 0.45 * math.cos(angle)
        vein_end_y = cy + length * 0.45 * math.sin(angle)
        draw.line([(cx, cy), (vein_end_x, vein_end_y)], fill=highlight, width=int(s*0.006))

    # 从研钵后方伸出两片叶子
    draw_leaf(draw, cx - s*0.08, s*0.42, s*0.22, -60, leaf_color, leaf_highlight)
    draw_leaf(draw, cx - s*0.02, s*0.38, s*0.26, -75, leaf_highlight, (140, 200, 100, 255))

    # === 装饰：底部金色弧线 ===
    arc_color = (200, 165, 80, 180)
    draw.arc(
        [s*0.12, s*0.82, s*0.88, s*1.08],
        start=200, end=340, fill=arc_color, width=int(s*0.012)
    )

    # === 装饰：顶部小圆点（药材颗粒） ===
    dots = [
        (cx + s*0.12, s*0.22, (220, 180, 90, 200)),
        (cx + s*0.20, s*0.30, (200, 160, 70, 180)),
        (cx + s*0.08, s*0.16, (230, 190, 100, 160)),
    ]
    for dx, dy, dc in dots:
        dr = s * 0.018
        draw.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], fill=dc)

    # 缩小到目标尺寸（抗锯齿）
    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    icon_dir = os.path.join(os.path.dirname(__file__), 'src-tauri', 'icons')
    os.makedirs(icon_dir, exist_ok=True)

    # 生成各尺寸 PNG
    sizes = [32, 128, 256]
    images = {}
    for sz in sizes:
        img = create_icon(sz)
        images[sz] = img
        if sz == 32:
            img.save(os.path.join(icon_dir, '32x32.png'))
            print(f"  32x32.png ({img.size})")
        elif sz == 128:
            img.save(os.path.join(icon_dir, '128x128.png'))
            print(f"  128x128.png ({img.size})")
        elif sz == 256:
            img.save(os.path.join(icon_dir, '128x128@2x.png'))
            print(f"  128x128@2x.png ({img.size})")

    # 生成 ICO（包含多尺寸）
    ico_images = [images[256], images[128], images[32]]
    ico_images[0].save(
        os.path.join(icon_dir, 'icon.ico'),
        format='ICO',
        sizes=[(256, 256), (128, 128), (32, 32)]
    )
    print(f"  icon.ico (multi-size)")

    # 生成 SVG 源文件（用于参考）
    svg_path = os.path.join(icon_dir, 'icon.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1e3c32"/>
      <stop offset="1" stop-color="#152d28"/>
    </linearGradient>
    <linearGradient id="bowl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#c83c2d"/>
      <stop offset="1" stop-color="#8a2418"/>
    </linearGradient>
    <linearGradient id="pestle" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#a07846"/>
      <stop offset="1" stop-color="#6e4f30"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="240" height="240" rx="40" fill="url(#bg)"/>
  <!-- 叶子 -->
  <g transform="translate(100,108) rotate(-75)">
    <ellipse cx="0" cy="0" rx="30" ry="11" fill="#5a8c3c"/>
    <line x1="-28" y1="0" x2="28" y2="0" stroke="#78b450" stroke-width="1.5"/>
  </g>
  <g transform="translate(92,112) rotate(-60)">
    <ellipse cx="0" cy="0" ry="26" rx="9" fill="#78b450"/>
    <line x1="-24" y1="0" x2="24" y2="0" stroke="#8ccc64" stroke-width="1.5"/>
  </g>
  <!-- 研杵 -->
  <rect x="130" y="36" width="9" height="86" rx="4" fill="url(#pestle)"/>
  <ellipse cx="134.5" cy="38" rx="5" ry="4" fill="#aa8256"/>
  <!-- 研钵 -->
  <path d="M 76 134 L 180 134 L 164 200 L 92 200 Z" fill="url(#bowl)"/>
  <ellipse cx="128" cy="134" rx="52" ry="8" fill="#641812"/>
  <ellipse cx="128" cy="133" rx="46" ry="5" fill="#3a0e0a"/>
  <!-- 底部装饰弧 -->
  <path d="M 36 220 Q 128 260 220 220" stroke="#c8a550" stroke-width="3" fill="none" opacity="0.6"/>
  <!-- 药材颗粒 -->
  <circle cx="160" cy="56" r="3" fill="#d4b45a" opacity="0.8"/>
  <circle cx="176" cy="72" r="2.5" fill="#b89438" opacity="0.7"/>
  <circle cx="148" cy="44" r="2" fill="#e6be64" opacity="0.6"/>
</svg>''')
    print(f"  icon.svg (source)")

    print("\n图标生成完成！")


if __name__ == '__main__':
    main()
