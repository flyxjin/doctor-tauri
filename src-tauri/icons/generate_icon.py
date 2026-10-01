# -*- coding: utf-8 -*-
"""生成中药材销售管理系统桌面图标

设计理念：「悬壶本草 · 现代版」（2026 改版，符合主流应用图标趋势）
- 大圆角方圆（squircle）翡翠渐变背景 — 现代应用图标标准形态
- 中央白色几何药葫芦 — 品牌符号「悬壶济世」的极简剪影，小尺寸清晰
- 束腰处浅翡翠本草叶 — 中草药意象的低饱和点缀
- 去除旧版的金色弧线与朱砂口，单一主色 + 强剪影

相比旧版「印章+本字」：用图形替代文字，16/32px 小尺寸下不再模糊。
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

# ==================== 配色（2026 现代化改版） ====================
# 翡翠渐变 + 白色几何药葫芦；弃用金色弧线与朱砂口，走向极简
BG_TOP = (16, 185, 129)      # #10B981 emerald-500
BG_BOTTOM = (4, 120, 87)     # #047857 emerald-700
GOURD_WHITE = (255, 255, 255)
GOURD_HIGHLIGHT = (255, 255, 255)
LEAF_DARK = (110, 231, 183)  # #6EE7B7 emerald-300
LEAF_LIGHT = (167, 243, 208) # #A7F3D0 emerald-200


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
    """渲染指定尺寸图标（4x 超采样抗锯齿）

    现代化设计语言：大圆角方圆底 + 翡翠对角渐变 + 白色几何药葫芦，
    去除装饰性弧线与多色点缀（主流应用图标趋势：少元素、强剪影）。
    """
    scale = 4
    s = size * scale
    img = make_bg(s, radius=int(s * 0.24))
    draw = ImageDraw.Draw(img)
    cx = s * 0.50

    # ========== 1. 葫芦口（白色小柱，与葫芦同色融为一体） ==========
    neck_w = s * 0.035
    draw.rounded_rectangle(
        [cx - neck_w, s * 0.135, cx + neck_w, s * 0.205],
        radius=max(2, int(neck_w * 0.5)), fill=GOURD_WHITE,
    )
    draw.ellipse(
        [cx - neck_w * 1.3, s * 0.125, cx + neck_w * 1.3, s * 0.155],
        fill=GOURD_WHITE,
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

    # 缩小到目标尺寸
    return img.resize((size, size), Image.LANCZOS)


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
    # icon.svg 不再由脚本写出：SVG 源文件直接编辑仓库内 icon.svg（避免脚本文件写入行为）
    print("图标生成完成。")


if __name__ == "__main__":
    main()
