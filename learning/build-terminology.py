#!/usr/bin/env python3
"""Generate detailed terminology Markdown and the HTML card fragment."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "learning"
DATA = json.loads((LEARN / "terminology.json").read_text(encoding="utf-8"))

LABELS = [
    ("official", "官方 / 仓库定义"),
    ("purpose", "用途"),
    ("principle", "原理"),
    ("scope", "作用范围"),
    ("where", "在 DSH 里"),
    ("confusion", "常见混淆"),
    ("verify", "最小验证"),
]

def md_block():
    lines = [
        "## 术语详解",
        "",
        "> 上面的表用于速查；这里逐条展开。官方定义优先引用仓库 glossary，其余标注为“仓库定义（按源码/文档归纳）”。",
        "",
    ]
    for i, term in enumerate(DATA, 1):
        lines.append("### 术语 " + str(i) + "：" + term["zh"] + "（" + term["en"] + "）")
        lines.append("")
        lines.append("**一句话**：" + term["oneLine"])
        lines.append("")
        for key, label in LABELS:
            lines.append("**" + label + "**：" + term[key])
            lines.append("")
        lines.append("**分类**：" + term["group"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def html_block():
    out = [
        '<div class="term-toolbar">',
        '<div><label for="term-search">搜索术语</label>',
        '<input id="term-search" type="search" placeholder="术语、职责、路径、易混点…" autocomplete="off"></div>',
        '<span id="term-count">' + str(len(DATA)) + ' 个术语</span>',
        '</div>',
        '<div class="term-grid" id="term-grid">',
    ]
    for i, term in enumerate(DATA, 1):
        haystack = " ".join(str(term[k]) for k in ["zh", "en", "group", "oneLine", "official", "purpose", "principle", "scope", "where", "confusion", "verify"]).lower()
        out.append('<article class="term-card" id="term-' + term["id"] + '" data-search="' + html.escape(haystack, quote=True) + '">')
        out.append('<div class="term-head"><div class="term-index">' + str(i).zfill(2) + '</div><div class="term-title"><h3>' + html.escape(term["zh"]) + ' <small>' + html.escape(term["en"]) + '</small></h3><p class="term-oneline">' + html.escape(term["oneLine"]) + '</p></div><span class="term-group">' + html.escape(term["group"]) + '</span></div>')
        out.append('<div class="term-fields">')
        for key, label in LABELS:
            value = html.escape(term[key])
            cls = "term-field" + (" term-where" if key == "where" else "") + (" term-warn" if key == "confusion" else "")
            out.append('<div class="' + cls + '"><span class="term-label">' + label + '</span><p>' + value + '</p></div>')
        out.append('</div></article>')
    out.append('</div>')
    out.append('<p class="term-empty" id="term-empty" hidden>没有匹配的术语，换个关键词试试。</p>')
    return "\n".join(out) + "\n"

md_path = LEARN / "01-terminology.zh.md"
text = md_path.read_text(encoding="utf-8")
block = md_block()
start = "<!-- TERMINOLOGY_DETAILS_START -->"
end = "<!-- TERMINOLOGY_DETAILS_END -->"
if start in text and end in text:
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), start + "\n\n" + block + "\n" + end, text, flags=re.S)
else:
    text = text.replace("## 6. 闭卷自测", "## 7. 闭卷自测")
    text = text.replace("## 7. 术语纠错练习", "## 8. 术语纠错练习")
    text = text.replace("## 7. 闭卷自测", start + "\n\n" + block + "\n" + end + "\n\n## 7. 闭卷自测")
md_path.write_text(text, encoding="utf-8")
(LEARN / "terminology-fragment.html").write_text(html_block(), encoding="utf-8")
print("updated", md_path, "and terminology-fragment.html")
