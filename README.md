# Tavia — 一个唯物主义者

蝴蝶结 + 报纸 + 雪的个人主页。

- 线上地址：<https://allllennnnnnnn.github.io/>
- 仓库：<https://github.com/allllennnnnnnn/allllennnnnnnn.github.io>

纯静态：HTML / CSS / 一个 JS 文件，没有构建步骤，没有框架，没有第三方脚本，没有统计。

```
index.html        页面结构（首屏 + 三块内容 + 结尾）
style.css         全部样式（蝴蝶结、报纸质感、排版、手机适配）
main.js           蝴蝶结上提、全站飘雪、结尾像素雪花、复制联系方式
img/              三张作品封面 + 图标
fonts/            子集化字体，共约 190 KB
tools/            生成插画的脚本（改图用）
.nojekyll         让 GitHub Pages 原样发布，不走 Jekyll
```

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 传到 GitHub Pages

1. 在 GitHub 新建仓库，例如 `tavia`（**不要**勾选「Add a README」，保持空仓库）。
2. 在本目录执行：

```bash
git init
git add .
git commit -m "Tavia homepage"
git branch -M main
git remote add origin https://github.com/<你的用户名>/tavia.git
git push -u origin main
```

3. 仓库 → Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`、目录 `/ (root)`，保存。
4. 一两分钟后访问 `https://<你的用户名>.github.io/tavia/`。

> 想让地址就是 `https://<你的用户名>.github.io/`，把仓库名改成 `<你的用户名>.github.io` 即可。

## 想改内容，改这几处

| 想改什么 | 在哪 |
| --- | --- |
| 首屏名字、一行话 | `index.html` 的 `.hero-name`、`.hero-line` |
| 自我介绍、档案表 | `index.html` 的 `#about`（`.headline`、`.lead-p`、`.record`） |
| 三件推荐作品 | `index.html` 的 `#works`：标题、年份、一句话、链接都在同一处 |
| 联系方式 | `index.html` 的 `#contact`，`data-copy="..."` 要和显示的文字一致 |
| 颜色 | `style.css` 开头 `:root` 的 `--blue / --night / --paper` |
| 雪的数量、速度 | `main.js` 的 `sizeSnow()` 里 `target` 与 `v` |
| 结尾雪花大小 | `style.css` 的 `#flake { width: min(88vw, 520px) }` |

### 换封面图

`img/cover-*.svg` 是脚本画的像素插画（600×840，5:7），**不是官方封面**，避免版权问题。
想换成真封面：把图片放进 `img/`，改 `index.html` 里对应的 `<img src="...">` 即可；比例建议 5:7。
想重画插画：编辑 `tools/make-covers.py`，然后

```bash
python3 tools/make-covers.py
```

### 关于生日

页面里把 `070116` 写作 `2007.01.16`。如果顺序不是「年月日」，改 `#about` 档案表里那一行即可。

## 字体

| 字体 | 用途 | 许可 |
| --- | --- | --- |
| Noto Serif SC 思源宋体 | 正文、标题、引文 | SIL Open Font License 1.1 |
| Instrument Serif | 报头、名字、英文斜体 | SIL Open Font License 1.1 |
| 缝合像素体 Fusion Pixel | 标签、日期、按钮、联系方式 | SIL Open Font License 1.1 |

字体都做过子集化（只保留页面用到的字）。之后如果加了很多新字、出现「豆腐块」，重新子集化一次：

```bash
pip install fonttools brotli
pyftsubset 原字体.woff2 --text-file=chars.txt --flavor=woff2 --output-file=fonts/xxx.woff2
```

像素字体请用 12px 的整数倍（12 / 24），否则会糊。

## 说明

- 飘雪是一层全屏 canvas：深色区域是白点，滚到纸上自动变成蓝墨点，所以整站都连贯。
- 首屏丝带随滚动向上卷走，把报纸露出来；结尾雪花随滚动从中心长出来，周围有碎雪绕行。
- 系统开启「减少动态效果」时动画会停，只留静态画面。
- 没有统计、没有 Cookie；`navigator.clipboard` 只用于复制微信号。
