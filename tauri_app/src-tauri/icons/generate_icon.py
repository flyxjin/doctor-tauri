"""生成中药材销售管理系统桌面图标

设计理念："东方本草" 篆刻印章
- 圆角方形深绿背景 (#1F4530) — 与 App 主题 siderBg 一致
- 中央朱砂红印章 (#C83C2D) + 白色"本"字 — 品牌符号
- 印章两侧装饰性叶片 — 中草药意象
- 底部金色弧线 — 点缀

输出：
- 32x32.png
- 128x128.png
- 128x128@2x.png  (256x256)
- icon.ico  (多分辨率嵌入)
- icon.svg  (矢量源)
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

# ==================== 配色 ====================
BG_TOP = (30, 69, 48)        # #1E4530 深草本绿（上）
BG_BOTTOM = (21, 45, 32)     # #152D20 深草本绿（下）
SEAL_RED = (200, 60, 45)     # #C83C2D 朱砂红
SEAL_DARK = (138, 36, 24)    # #8A2418 暗朱砂
LEAF_DARK = (90, 140, 60)    # #5A8C3C 深叶绿
LEAF_LIGHT = (120, 180, 80)  # #78B450 亮叶绿
GOLD = (200, 165, 80)        # #C8A550 金色
WHITE = (253, 250, 245)      # #FDFAF5 米白（与 headerBg 一致）


def lerp_color(c1, c2, t):
    """线性插值两个颜色"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def make_rounded_gradient_bg(size, radius):
    """生成圆角渐变背景"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (size, size))
    for y in range(size):
        t = y / max(size - 1, 1)
        color = lerp_color(BG_TOP, BG_BOTTOM, t)
        for x in range(size):
            grad.putpixel((x, y), color + (255,))
    # 圆角遮罩
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)
    return img


def draw_leaf(draw, cx, cy, length, width, angle_deg, color, vein_color):
    """绘制一片叶子（椭圆 + 主脉）"""
    cx, cy = int(cx), int(cy)
    # 用多边形近似旋转椭圆
    n = 24
    pts = []
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    for i in range(n):
        t = 2 * math.pi * i / n
        x = length * math.cos(t)
        y = width * math.sin(t)
        # 旋转 + 平移
        rx = x * cos_a - y * sin_a + cx
        ry = x * sin_a + y * cos_a + cy
        pts.append((int(rx), int(ry)))
    draw.polygon(pts, fill=color)
    # 主脉
    vx = int(length * cos_a + cx)
    vy = int(length * sin_a + cy)
    vx2 = int(-length * cos_a + cx)
    vy2 = int(-length * sin_a + cy)
    draw.line([(vx2, vy2), (vx, vy)], fill=vein_color, width=max(1, int(width * 0.15)))


def draw_seal(draw, cx, cy, half, char_font):
    """绘制朱砂印章 + 白色"本"字"""
    cx, cy, half = int(cx), int(cy), int(half)
    # 印章主体（带轻微圆角的方形）
    seal_rect = [cx - half, cy - half, cx + half, cy + half]
    draw.rounded_rectangle(seal_rect, radius=max(2, half // 8), fill=SEAL_RED)
    # 内边框（暗朱砂细线）
    inset = max(2, half // 12)
    draw.rounded_rectangle(
        [cx - half + inset, cy - half + inset, cx + half - inset, cy + half - inset],
        radius=max(1, half // 10),
        outline=SEAL_DARK,
        width=max(1, half // 32),
    )
    # "本"字
    if char_font is not None:
        # 测量字号
        text = "本"
        bbox = draw.textbbox((0, 0), text, font=char_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = int(cx - tw / 2 - bbox[0])
        ty = int(cy - th / 2 - bbox[1])
        draw.text((tx, ty), text, font=char_font, fill=WHITE)


def find_cjk_font(size):
    """尝试加载系统中文字体"""
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",       # 微软雅黑
        "C:/Windows/Fonts/msyhbd.ttc",     # 微软雅黑 Bold
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
        "C:/Windows/Fonts/Deng.ttf",       # 等线
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return None


def render_icon(size):
    """渲染指定尺寸的图标"""
    img = make_rounded_gradient_bg(size, radius=int(size * 0.18))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2

    # 1. 印章两侧的装饰叶子（左下、右上对称）
    leaf_len = size * 0.18
    leaf_wid = size * 0.07
    # 左下叶子
    draw_leaf(
        draw,
        cx - size * 0.32, cy + size * 0.28,
        leaf_len, leaf_wid,
        angle_deg=-40,
        color=LEAF_DARK,
        vein_color=LEAF_LIGHT,
    )
    # 右上叶子
    draw_leaf(
        draw,
        cx + size * 0.32, cy - size * 0.28,
        leaf_len, leaf_wid,
        angle_deg=140,
        color=LEAF_DARK,
        vein_color=LEAF_LIGHT,
    )

    # 2. 中央朱砂印章
    seal_half = size * 0.28
    font_size = int(seal_half * 1.5)
    char_font = find_cjk_font(font_size)
    draw_seal(draw, cx, cy, seal_half, char_font)

    # 3. 底部金色弧线装饰
    arc_box = [int(size * 0.14), int(size * 0.78), int(size * 0.86), int(size * 1.08)]
    draw.arc(arc_box, start=200, end=340, fill=GOLD, width=max(1, int(size * 0.012)))

    return img


def write_svg(path):
    """同步输出 SVG 矢量源（与位图设计一致）"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1E4530"/>
      <stop offset="1" stop-color="#152D20"/>
    </linearGradient>
  </defs>
  <rect x="8" y="8" width="240" height="240" rx="44" fill="url(#bg)"/>
  <!-- 左下叶子 -->
  <g transform="translate(70,180) rotate(-40)">
    <ellipse cx="0" cy="0" rx="46" ry="18" fill="#5A8C3C"/>
    <line x1="-42" y1="0" x2="42" y2="0" stroke="#78B450" stroke-width="2.5"/>
  </g>
  <!-- 右上叶子 -->
  <g transform="translate(186,76) rotate(140)">
    <ellipse cx="0" cy="0" rx="46" ry="18" fill="#5A8C3C"/>
    <line x1="-42" y1="0" x2="42" y2="0" stroke="#78B450" stroke-width="2.5"/>
  </g>
  <!-- 朱砂印章 -->
  <rect x="72" y="72" width="112" height="112" rx="14" fill="#C83C2D"/>
  <rect x="78" y="78" width="100" height="100" rx="10" fill="none" stroke="#8A2418" stroke-width="3"/>
  <!-- "本"字 -->
  <text x="128" y="128" font-family="'Microsoft YaHei','SimHei',sans-serif" font-size="92"
        font-weight="bold" fill="#FDFAF5" text-anchor="middle" dominant-baseline="central">本</text>
  <!-- 底部金色弧线 -->
  <path d="M 36 220 Q 128 260 220 220" stroke="#C8A550" stroke-width="3" fill="none" opacity="0.7"/>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    # 渲染各尺寸 PNG
    sizes = {
        "32x32.png": 32,
        "128x128.png": 128,
        "128x128@2x.png": 256,
    }
    images = {}
    for name, sz in sizes.items():
        img = render_icon(sz)
        img.save(os.path.join(here, name))
        images[sz] = img
        print(f"  生成 {name} ({sz}x{sz})")

    # 生成 ICO（嵌入多分辨率：16/24/32/48/64/128/256）
    # PIL ICO 保存：base image 自动按 sizes 列表缩放，append_images 提供高保真源
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base = images[256].convert("RGBA")  # 用最大尺寸作为 base
    base.save(
        os.path.join(here, "icon.ico"),
        format="ICO",
        sizes=ico_sizes,
    )
    ico_size = os.path.getsize(os.path.join(here, "icon.ico"))
    print(f"  生成 icon.ico (嵌入 {len(ico_sizes)} 个尺寸, {ico_size / 1024:.1f} KB)")

    # 输出 SVG 矢量源
    write_svg(os.path.join(here, "icon.svg"))
    print("  生成 icon.svg")

    print("\n图标生成完成。")


if __name__ == "__main__":
    main()
