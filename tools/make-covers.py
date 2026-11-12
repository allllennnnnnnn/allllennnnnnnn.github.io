#!/usr/bin/env python3
"""
生成 img/ 里的像素插画（纯方块 SVG，无位图依赖）。
运行：python3 tools/make-covers.py

网格：75×105 个像素块，输出 600×840（5:7），shape-rendering=crispEdges。
"""
import math, random, os

OUT = os.path.join(os.path.dirname(__file__), "..", "img")
W, H = 75, 105          # 网格
S = 8                   # 每格像素

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def mix(c1, c2, t):
    a, b = hex2rgb(c1), hex2rgb(c2)
    return "#" + "".join(f"{round(a[i] + (b[i]-a[i])*t):02x}" for i in range(3))


class Pix:
    def __init__(self):
        self.g = {}          # 全部存不透明色：透明一律先和底色混合
        self.bg = "#000000"

    def px(self, x, y, c, a=1.0):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            if a >= 0.999:
                self.g[(x, y)] = c
            else:
                base = self.g.get((x, y), self.bg)
                self.g[(x, y)] = mix(base, c, a)

    def rect(self, x, y, w, h, c, a=1.0):
        for j in range(int(y), int(y + h)):
            for i in range(int(x), int(x + w)):
                self.px(i, j, c, a)

    def hrun(self, x, y, w, c, a=1.0):
        self.rect(x, y, w, 1, c, a)

    def disc(self, cx, cy, r, c, a=1.0, soft=False):
        for j in range(int(cy - r), int(cy + r) + 1):
            for i in range(int(cx - r), int(cx + r) + 1):
                d = math.hypot(i - cx, j - cy)
                if d <= r:
                    if soft and d > r - 1.2:
                        self.px(i, j, c, a * 0.55)
                    else:
                        self.px(i, j, c, a)

    def dither(self, x, y, w, h, c, a=1.0, step=2, phase=0):
        for j in range(int(y), int(y + h)):
            for i in range(int(x), int(x + w)):
                if (i + j + phase) % step == 0:
                    self.px(i, j, c, a)

    def fade(self, y0, y1, c1, c2, power=1.0):
        n = max(1, y1 - y0)
        for y in range(int(y0), int(y1)):
            t = ((y - y0) / n) ** power
            c = mix(c1, c2, t)
            for x in range(W):
                self.px(x, y, c)

    def vgrad(self, y0, y1, colors):
        n = max(1, y1 - y0)
        for y in range(int(y0), int(y1)):
            t = (y - y0) / n * (len(colors) - 1)
            k = min(len(colors) - 1, int(t))
            c = colors[k]
            for x in range(W):
                self.px(x, y, c)

    def svg(self, bg):
        runs = []
        for y in range(H):
            x = 0
            while x < W:
                key = self.g.get((x, y))
                if not key:
                    x += 1
                    continue
                c = key
                n = 1
                while x + n < W and self.g.get((x + n, y)) == c:
                    n += 1
                runs.append((x, y, n, 1, c, 1.0))
                x += n
        parts = [f'<rect width="{W*S}" height="{H*S}" fill="{bg}"/>']
        last = None
        buf = []
        for (x, y, w, h, c, a) in runs:
            op = '' if a >= 0.999 else f' opacity="{a:g}"'
            buf.append(f'<rect x="{x*S}" y="{y*S}" width="{w*S}" height="{h*S}" fill="{c}"{op}/>')
        body = "".join(buf)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*S} {H*S}" '
                f'shape-rendering="crispEdges" role="img">'
                f'<defs><radialGradient id="vg" cx="50%" cy="42%" r="76%">'
                f'<stop offset="52%" stop-color="#000" stop-opacity="0"/>'
                f'<stop offset="100%" stop-color="#02080f" stop-opacity=".55"/>'
                f'</radialGradient></defs>'
                + parts[0] + body +
                f'<rect width="{W*S}" height="{H*S}" fill="url(#vg)"/></svg>')


# ---------------------------------------------------------------- 1. 逆流的河
def river():
    p = Pix(); p.bg = "#020810"
    p.fade(0, 37, "#040f1d", "#0a2438", 1.4)

    # 月
    p.disc(52, 11, 7, "#cfe6f6", .12)
    p.disc(52, 11, 5, "#ffffff", .97)

    random.seed(4)
    for _ in range(14):
        p.px(random.randrange(W), random.randrange(0, 33), "#dff0fb", random.choice([.2, .35]))

    # 远岸
    p.rect(0, 36, W, 2, "#030c15")

    # 水：一条条细渐变，没有硬边
    p.fade(38, 105, "#2f7ba6", "#04101b", .85)

    # 月光落在水面上：一团横着铺开的光，不是柱子
    random.seed(31)
    for yy in range(39, 72):
        t = (yy - 39) / 33
        wdt = int(16 - t * 10)
        cx = 52 + random.randint(-1, 1)
        for k in range(wdt):
            if random.random() < .55:
                p.px(cx - wdt // 2 + k, yy, "#cfe6f6", round(.20 - t * .16, 2))
    for _ in range(26):
        x = 52 + random.randint(-7, 7)
        yy = random.randrange(40, 60)
        p.px(x, yy, "#eaf6ff", round(random.uniform(.2, .45), 2))

    # 水纹
    random.seed(21)
    for _ in range(60):
        yy = random.randrange(39, 101)
        x = random.randrange(-4, W - 6)
        ln = random.choice([4, 6, 8, 11])
        c = random.choice(["#6fb3d8", "#a8d3ea"])
        a = round(random.uniform(.10, .28), 2) * (1 - (yy - 39) / 70)
        p.hrun(x, yy, ln, c, max(.04, a))

    # 纸船
    p.rect(30, 78, 10, 2, "#ffffff", .96)
    p.rect(32, 80, 6, 1, "#b9d6e8", .7)
    p.rect(34, 74, 2, 4, "#ffffff", .9)
    p.hrun(28, 81, 14, "#dff0fb", .10)

    # 雨
    random.seed(8)
    for _ in range(18):
        x = random.randrange(W)
        yy = random.randrange(2, 32)
        for k in range(random.choice([3, 4, 5])):
            p.px(x, yy + k, "#bcd9ee", round(random.uniform(.10, .26), 2))

    p.fade(96, 105, "#04101b", "#020810", 1.0)
    return p.svg("#020810")


# ---------------------------------------------------------------- 2. 窗与夜
def tabun():
    p = Pix(); p.bg = "#040d18"
    p.rect(0, 0, W, H, "#040d18")

    # 玻璃（先铺底色，不然后面画的窗外会被盖住）
    p.rect(5, 5, 65, 62, "#04121f")

    # 窗外的夜空
    p.fade(5, 40, "#0d2f4d", "#1f5c86", .9)
    p.fade(40, 67, "#1f5c86", "#2f7ba6", .8)

    # 远处的城
    random.seed(12)
    x = 0
    while x < W:
        bw = random.choice([5, 7, 9])
        bh = random.choice([12, 18, 24, 30])
        p.rect(x, 66 - bh, bw, bh, "#071a2c")
        for j in range(66 - bh + 1, 64, 3):
            for i in range(x + 1, x + bw - 1, 2):
                if random.random() < .45:
                    p.px(i, j, "#9fd0ee", round(random.uniform(.35, .85), 2))
        x += bw + 1

    # 对面一扇亮着的窗
    p.rect(20, 42, 10, 9, "#6fa8cd", .9)
    p.rect(21, 43, 4, 3, "#ffffff", .95)
    p.rect(26, 43, 3, 3, "#dff0fb", .8)
    p.rect(21, 47, 4, 3, "#dff0fb", .6)
    p.disc(25, 46, 9, "#bfe0f5", .10)

    # 街灯
    p.disc(58, 56, 7, "#bfe0f5", .08)
    p.disc(58, 56, 2, "#eaf6ff", .7)
    p.rect(58, 56, 1, 10, "#071a2c")

    # 窗框：四条边 + 十字压条（不能整块填，否则把窗外的景盖掉）
    p.rect(0, 0, W, 5, "#0a2842")
    p.rect(0, 66, W, 5, "#0a2842")
    p.rect(0, 0, 5, 71, "#0a2842")
    p.rect(70, 0, 5, 71, "#0a2842")
    p.rect(0, 0, W, 2, "#16456c")
    p.rect(0, 0, 2, 71, "#16456c")
    p.rect(37, 5, 2, 61, "#0a2842")
    p.rect(5, 33, 65, 2, "#0a2842")
    p.rect(38, 5, 1, 61, "#2c6ea6", .35)

    # 窗台
    p.rect(0, 69, W, 3, "#0d3352")
    p.rect(0, 72, W, 2, "#030b14")

    # 窗台上的杯子和草
    p.rect(10, 65, 4, 4, "#0b2c48")
    p.rect(10, 65, 4, 1, "#5f9fdc", .4)
    p.rect(58, 65, 3, 4, "#0b2c48")
    p.px(59, 64, "#5f9fdc", .5); p.px(60, 63, "#5f9fdc", .4)

    # 地面：窗口光落下来的一滩
    p.fade(73, 105, "#061423", "#02080f", 1.1)
    random.seed(5)
    for y in range(74, 100):
        for x in range(14, 60):
            if random.random() < .10:
                p.px(x, y, "#2a6ea6", round(.14 * (1 - (y - 74) / 26), 2))

    # 玻璃上的雨
    random.seed(3)
    for _ in range(30):
        x = random.randrange(7, 68)
        y = random.randrange(7, 62)
        for k in range(random.choice([2, 3])):
            p.px(x, y + k, "#cfe8f8", round(random.uniform(.10, .26), 2))

    # 窗帘
    p.rect(0, 0, 3, 74, "#061624")
    p.rect(2, 0, 1, 74, "#16456c", .3)
    return p.svg("#040d18")


# ---------------------------------------------------------------- 3. 天空
def weather():
    p = Pix(); p.bg = "#04121f"
    p.fade(0, 74, "#04121f", "#1f6a97", .9)

    # 太阳
    p.disc(41, 13, 11, "#bfe0f5", .07)
    p.disc(41, 13, 8, "#eaf6ff", .10)
    p.disc(41, 13, 6, "#ffffff", .97)

    # 云：平底圆顶，颜色随高度一阶一阶变亮
    CLOUD = ["#2f6a93", "#3d7ea6", "#5f9cc4", "#8fc2e0", "#b9d9ee", "#e8f5ff"]

    def cumulus(cx, base_y, half, height, seed):
        random.seed(seed)
        bumps = [(cx - half * .52, height * .70, half * .52),
                 (cx + .5, height * 1.00, half * .62),
                 (cx + half * .50, height * .66, half * .46)]
        for x in range(int(cx - half), int(cx + half) + 1):
            hh = 0.0
            for (bx, bh, bw) in bumps:
                d = (x - bx) / bw
                if abs(d) < 1:
                    hh = max(hh, bh * math.sqrt(1 - d * d))
            if hh < 1:
                continue
            for y in range(int(base_y - hh), int(base_y) + 1):
                t = (base_y - y) / max(1.0, hh)
                c = CLOUD[min(len(CLOUD) - 1, int(t * (len(CLOUD) - 1) + .35))]
                p.px(x, y, c)
        # 底部压深，像云影
        for x in range(int(cx - half), int(cx + half) + 1):
            p.px(x, base_y, "#2b6489")
            p.px(x, base_y + 1, "#255c80", .7)

    cumulus(20, 84, 18, 12, 3)
    cumulus(58, 90, 15, 9, 5)
    cumulus(39, 76, 12, 9, 9)

    # 雨
    random.seed(31)
    for _ in range(44):
        x = random.randrange(0, W)
        y = random.randrange(44, 78)
        ln = random.choice([2, 3])
        for k in range(ln):
            p.px(x + k * .5, y + k, "#dff1fd", round(random.uniform(.12, .34), 2))

    # 城市剪影
    p.rect(0, 99, W, 6, "#04101b")
    random.seed(8)
    x = 0
    while x < W:
        bw = random.choice([4, 6, 8])
        bh = random.choice([3, 6, 9])
        p.rect(x, 99 - bh, bw, bh, "#04101b")
        x += bw + 1
    return p.svg("#04121f")


# ---------------------------------------------------------------- 人像
def portrait():
    p = Pix(); p.bg = "#040f1c"
    p.vgrad(0, 74, ["#040f1c", "#061726", "#082236", "#0a2b42"])
    random.seed(13)
    for _ in range(40):
        p.px(random.randrange(W), random.randrange(0, 70), "#cfe6f8", random.choice([.2, .3, .45]))

    # 远处的城
    random.seed(23)
    x = 0
    while x < W:
        bw = random.choice([3, 4, 6])
        bh = random.choice([3, 4, 6, 8])
        p.rect(x, 70 - bh, bw, bh, "#061423")
        x += bw
    # 雪原
    p.vgrad(74, 105, ["#0c2a44", "#0a2137", "#071829"])
    random.seed(2)
    for y in range(76, 104, 2):
        for x in range(W):
            if random.random() < .30:
                p.px(x, y, "#12395c", round(random.uniform(.25, .6), 2))

    # 人
    p.rect(34, 42, 5, 5, "#030a12")
    p.rect(36, 47, 2, 1, "#030a12")
    p.rect(32, 48, 9, 3, "#030a12")
    p.rect(30, 51, 13, 13, "#030a12")
    p.rect(31, 64, 4, 12, "#030a12")
    p.rect(38, 64, 4, 12, "#030a12")
    p.rect(29, 52, 2, 10, "#030a12")
    p.rect(42, 52, 2, 10, "#030a12")
    # 大衣的蓝与围巾
    p.rect(30, 51, 13, 2, "#12395c")
    p.rect(36, 53, 1, 10, "#0e2b46")
    p.rect(32, 46, 9, 2, "#2c6ea6")
    p.rect(33, 48, 2, 5, "#2c6ea6", .85)

    # 脚印
    p.rect(28, 70, 2, 1, "#071a2b"); p.rect(25, 73, 2, 1, "#071a2b"); p.rect(22, 76, 2, 1, "#071a2b")

    # 飘雪
    random.seed(6)
    for _ in range(70):
        s = random.choice([1, 1, 1, 2])
        p.rect(random.randrange(W - s), random.randrange(H - s), s, s,
               "#e8f3fb", round(random.uniform(.2, .85), 2))
    return p.svg("#040f1c")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("portrait.svg", portrait),
                     ("cover-river.svg", river),
                     ("cover-tabun.svg", tabun),
                     ("cover-weathering.svg", weather)]:
        path = os.path.join(OUT, name)
        open(path, "w", encoding="utf-8").write(fn())
        print(name, os.path.getsize(path) // 1024, "KB")
