#!/usr/bin/env python3
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "learning"

CSS = """
:root {
  --bg: #f5f7fb;
  --bg-soft: #eef2f9;
  --panel: #ffffff;
  --ink: #162033;
  --muted: #63708a;
  --line: #dfe6f1;
  --accent: #4f46e5;
  --accent-2: #0f766e;
  --accent-3: #b45309;
  --code-bg: #101827;
  --code-ink: #dbeafe;
  --success: #047857;
  --warning: #b45309;
  --shadow: 0 18px 50px rgba(22, 32, 51, .08);
  --radius: 18px;
  --sidebar: 278px;
}
[data-theme="dark"] {
  --bg: #0b1120;
  --bg-soft: #111a2e;
  --panel: #121c31;
  --ink: #e8eef9;
  --muted: #9aa8c0;
  --line: #26344f;
  --accent: #8b8cf8;
  --accent-2: #5eead4;
  --accent-3: #fbbf24;
  --code-bg: #050a14;
  --code-ink: #dbeafe;
  --success: #34d399;
  --warning: #fbbf24;
  --shadow: 0 22px 60px rgba(0, 0, 0, .35);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(1100px 500px at 8% -8%, rgba(79, 70, 229, .14), transparent 60%),
    radial-gradient(900px 480px at 95% 4%, rgba(15, 118, 110, .12), transparent 55%),
    var(--bg);
  color: var(--ink);
  font-family: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", system-ui, -apple-system, "Segoe UI", sans-serif;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.app { display: grid; grid-template-columns: var(--sidebar) minmax(0, 1fr); min-height: 100vh; }
.sidebar {
  position: sticky; top: 0; height: 100vh; overflow-y: auto;
  padding: 26px 20px 30px;
  border-right: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel) 88%, transparent);
  backdrop-filter: blur(12px);
}
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 26px; }
.brand-mark {
  width: 46px; height: 46px; border-radius: 14px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #fff; font-weight: 800; letter-spacing: -.04em;
  box-shadow: 0 10px 24px rgba(79, 70, 229, .25);
}
.brand strong { display: block; font-size: 17px; letter-spacing: -.02em; }
.brand small { display: block; color: var(--muted); font-size: 12px; margin-top: 2px; }
.nav-label { color: var(--muted); font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 18px 10px 8px; }
.nav { display: grid; gap: 4px; }
.nav a {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 11px;
  color: var(--muted); font-size: 14px; font-weight: 600;
}
.nav a:hover { background: var(--bg-soft); color: var(--ink); text-decoration: none; }
.nav a.active { background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--accent); }
.nav-num {
  width: 24px; height: 24px; border-radius: 8px;
  display: grid; place-items: center; font-size: 11px;
  background: var(--bg-soft); color: var(--muted);
}
.nav a.active .nav-num { background: var(--accent); color: #fff; }
.progress-box { margin-top: 24px; padding: 14px; border: 1px solid var(--line); border-radius: 14px; background: var(--bg-soft); }
.progress-top { display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 8px; }
.progress-track { height: 8px; border-radius: 99px; background: var(--line); overflow: hidden; }
.progress-fill { height: 100%; width: 0; background: linear-gradient(90deg, var(--accent), var(--accent-2)); transition: width .25s ease; }
.side-actions { display: flex; gap: 8px; margin-top: 14px; }
.side-btn, .btn {
  border: 1px solid var(--line); background: var(--panel); color: var(--ink);
  border-radius: 10px; padding: 8px 11px; font: inherit; font-size: 12px; cursor: pointer;
}
.side-btn:hover, .btn:hover { border-color: var(--accent); color: var(--accent); }
.main { min-width: 0; }
.topbar {
  display: none; position: sticky; top: 0; z-index: 20;
  align-items: center; justify-content: space-between;
  padding: 12px 16px; border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel) 92%, transparent); backdrop-filter: blur(10px);
}
.topbar button { border: 1px solid var(--line); background: var(--panel); border-radius: 9px; padding: 7px 10px; color: var(--ink); }
.wrap { max-width: 1120px; margin: 0 auto; padding: 40px 42px 80px; }
.hero {
  position: relative; overflow: hidden;
  border-radius: 26px; padding: 38px 38px 32px;
  background: linear-gradient(135deg, #1f2554 0%, #343a86 45%, #0f766e 100%);
  color: #fff; box-shadow: var(--shadow);
}
.hero::after {
  content: ""; position: absolute; width: 340px; height: 340px; right: -100px; top: -130px;
  border-radius: 50%; background: rgba(255,255,255,.12); filter: blur(2px);
}
.eyebrow { font-size: 12px; letter-spacing: .16em; text-transform: uppercase; opacity: .78; font-weight: 700; }
.hero h1 { font-size: clamp(28px, 4.2vw, 48px); line-height: 1.15; margin: 10px 0 12px; letter-spacing: -.045em; }
.hero p { max-width: 760px; margin: 0; color: rgba(255,255,255,.82); font-size: 15px; }
.hero-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.pill { border: 1px solid rgba(255,255,255,.22); background: rgba(255,255,255,.10); padding: 6px 10px; border-radius: 99px; font-size: 12px; color: #fff; }
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 18px; }
.stat { background: var(--panel); border: 1px solid var(--line); border-radius: 15px; padding: 14px 15px; box-shadow: 0 8px 22px rgba(22,32,51,.04); }
.stat strong { display: block; font-size: 22px; letter-spacing: -.03em; }
.stat span { color: var(--muted); font-size: 12px; }
.section {
  margin-top: 26px; padding: 30px 32px;
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  box-shadow: var(--shadow); scroll-margin-top: 22px;
}
.chapter { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 8px; }
.chapter-left { display: flex; gap: 12px; align-items: flex-start; }
.chapter-num {
  width: 38px; height: 38px; flex: 0 0 auto; border-radius: 12px;
  display: grid; place-items: center; background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #fff; font-weight: 800; font-size: 13px; box-shadow: 0 8px 18px rgba(79,70,229,.2);
}
.chapter h2 { margin: 0; font-size: 23px; letter-spacing: -.03em; }
.chapter p { margin: 2px 0 0; color: var(--muted); font-size: 13px; }
.done-btn { white-space: nowrap; }
.done-btn.done { background: color-mix(in srgb, var(--success) 14%, transparent); border-color: color-mix(in srgb, var(--success) 45%, var(--line)); color: var(--success); }
.content { font-size: 15px; }
.content > h1:first-child { display: none; }
.content h2 { margin: 32px 0 10px; font-size: 20px; letter-spacing: -.025em; scroll-margin-top: 20px; }
.content h3 { margin: 24px 0 8px; font-size: 16px; }
.content p { margin: 10px 0; }
.content ul, .content ol { padding-left: 22px; margin: 10px 0; }
.content li { margin: 5px 0; }
.content strong { color: var(--ink); }
.content code {
  font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
  font-size: .88em; background: var(--bg-soft); border: 1px solid var(--line);
  padding: 1px 5px; border-radius: 6px;
}
.content pre {
  position: relative; margin: 16px 0; padding: 18px 18px;
  background: var(--code-bg); color: var(--code-ink);
  border-radius: 14px; overflow: auto; line-height: 1.6;
  border: 1px solid rgba(255,255,255,.08);
}
.content pre code { background: transparent; border: 0; padding: 0; color: inherit; font-size: 12.5px; }
.copy-code {
  position: absolute; right: 10px; top: 8px; border: 1px solid rgba(255,255,255,.22);
  background: rgba(255,255,255,.10); color: #fff; border-radius: 7px; padding: 3px 7px;
  font-size: 11px; cursor: pointer; opacity: .65;
}
.copy-code:hover { opacity: 1; }
.content table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13.5px; }
.content th, .content td { border: 1px solid var(--line); padding: 9px 10px; vertical-align: top; text-align: left; }
.content th { background: var(--bg-soft); font-weight: 700; }
.table-wrap { overflow-x: auto; margin: 16px 0; }
.table-wrap table { margin: 0; }
.content blockquote { margin: 16px 0; padding: 10px 16px; border-left: 4px solid var(--accent); background: var(--bg-soft); color: var(--muted); border-radius: 0 10px 10px 0; }
.content hr { border: 0; border-top: 1px solid var(--line); margin: 26px 0; }
.content a { font-weight: 600; }
.diagram {
  margin: 18px 0; padding: 18px; border: 1px dashed color-mix(in srgb, var(--accent) 40%, var(--line));
  border-radius: 16px; background: var(--bg-soft);
}
.flow-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: center; }
.flow-box { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 7px 10px; font-size: 12px; font-weight: 700; box-shadow: 0 4px 10px rgba(22,32,51,.04); }
.flow-box.primary { border-color: var(--accent); color: var(--accent); }
.flow-box.green { border-color: var(--accent-2); color: var(--accent-2); }
.flow-arrow { color: var(--muted); font-weight: 800; }
.flow-label { text-align: center; color: var(--muted); font-size: 11px; margin: 4px 0; }
.quiz-card, .answer-card {
  margin: 18px 0 24px; padding: 20px; border-radius: 16px;
  border: 1px solid color-mix(in srgb, var(--accent) 28%, var(--line));
  background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 7%, var(--panel)), var(--panel));
}
.quiz-card h2, .answer-card h2 { margin: 0 0 4px; font-size: 18px; }
.quiz-card .hint, .answer-card .hint { color: var(--muted); font-size: 12.5px; margin: 0 0 14px; }
.q { margin: 12px 0; }
.q label { display: block; font-size: 13.5px; font-weight: 700; margin-bottom: 5px; }
.q textarea, .big-answer {
  width: 100%; min-height: 58px; resize: vertical;
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel); color: var(--ink);
  padding: 9px 10px; font: inherit; font-size: 13.5px; line-height: 1.55;
}
.q textarea:focus, .big-answer:focus { outline: 2px solid color-mix(in srgb, var(--accent) 45%, transparent); border-color: var(--accent); }
.big-answer { min-height: 180px; margin-top: 6px; }
.row-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 12px; }
.status { color: var(--muted); font-size: 12px; }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn.primary:hover { color: #fff; filter: brightness(1.05); }
details.answer-box { margin-top: 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--bg-soft); padding: 10px 14px; }
details.answer-box summary { cursor: pointer; font-weight: 700; color: var(--accent-3); }
details.answer-box[open] { padding-bottom: 16px; }
.footer { color: var(--muted); font-size: 12px; text-align: center; padding: 26px 0 0; }
.kbd { font-family: monospace; background: var(--bg-soft); border: 1px solid var(--line); border-bottom-width: 2px; border-radius: 5px; padding: 1px 5px; font-size: .85em; }
@media (max-width: 900px) {
  :root { --sidebar: 0px; }
  .app { display: block; }
  .sidebar { position: fixed; z-index: 30; left: 0; top: 0; width: 280px; transform: translateX(-102%); transition: transform .2s ease; }
  .sidebar.open { transform: translateX(0); box-shadow: 0 0 60px rgba(0,0,0,.25); }
  .topbar { display: flex; }
  .wrap { padding: 24px 16px 60px; }
  .hero { padding: 28px 22px; border-radius: 20px; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .section { padding: 22px 18px; }
  .chapter { flex-direction: column; }
}
@media (max-width: 520px) {
  .stat-grid { grid-template-columns: 1fr; }
  .chapter h2 { font-size: 20px; }
}
@media print {
  .sidebar, .topbar, .done-btn, .side-actions, .row-actions, .copy-code { display: none !important; }
  .app { display: block; }
  .wrap { max-width: none; padding: 0; }
  .section, .hero { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
}
"""

DIAGRAM = """
<div class="diagram" role="img" aria-label="DSH 架构总览">
  <div class="flow-label">载体</div>
  <div class="flow-row"><span class="flow-box">CLI</span><span class="flow-box">Desktop</span><span class="flow-box">Web</span><span class="flow-box">SDK / ACP</span></div>
  <div class="flow-label">↓</div>
  <div class="flow-label">装配层</div>
  <div class="flow-row"><span class="flow-box primary">app-boot / Loader</span><span class="flow-box">profile + bundles + patches</span></div>
  <div class="flow-label">↓</div>
  <div class="flow-label">Node Host：同一棵 Cordis 插件树</div>
  <div class="flow-row">
    <span class="flow-box green">agent-loop</span>
    <span class="flow-box green">Session 日志</span>
    <span class="flow-box green">tools registry</span>
    <span class="flow-box green">LLM adapters</span>
    <span class="flow-box green">web host / API</span>
  </div>
  <div class="flow-label">↓</div>
  <div class="flow-row"><span class="flow-box">shell</span><span class="flow-box">fs / sandbox</span><span class="flow-box">python / Office</span><span class="flow-box">MCP</span></div>
  <div class="flow-label">Client 只通过 HTTP/WS 消费投影</div>
</div>
"""

MARKDOWN_EXT = ["fenced_code", "tables", "sane_lists"]

def read_md(name):
    return (LEARN / name).read_text(encoding="utf-8")

def render_md(name):
    text = read_md(name)
    rendered = markdown.markdown(text, extensions=MARKDOWN_EXT)
    rendered = re.sub(r"<h1>.*?</h1>", "", rendered, count=1, flags=re.S)
    links = {
        "README.zh.md": "#overview",
        "01-terminology.zh.md": "#m1",
        "02-architecture.zh.md": "#m2",
        "03-code-implementation.zh.md": "#m3",
        "04-transfer-assessment.zh.md": "#m4",
        "answer-key.zh.md": "#answers",
        "docs/linux/BUILD.zh.md": "https://github.com/lsp725jk/deepseek-harness-linux/blob/main/docs/linux/BUILD.zh.md",
        "docs/linux/ROADMAP.zh.md": "https://github.com/lsp725jk/deepseek-harness-linux/blob/main/docs/linux/ROADMAP.zh.md",
        "docs/analysis/deepseek-harness-architecture.zh.md": "https://github.com/lsp725jk/deepseek-harness-linux/blob/main/docs/analysis/deepseek-harness-architecture.zh.md",
    }
    for old, new in links.items():
        rendered = rendered.replace('href="' + old + '"', 'href="' + new + '"')
    if name == "02-architecture.zh.md":
        rendered = re.sub(r'<pre><code class="language-mermaid">.*?</code></pre>', DIAGRAM, rendered, count=1, flags=re.S)
    return rendered

DIAGNOSTIC = [
    "Turn 和 Step 的区别？一个 turn 可以有几个 step？",
    "Profile、Bundle、Patch 谁覆盖谁？覆盖 config 是深合并还是替换？",
    "Plugin、Service、Tool 三者关系？各举一个 DSH 例子。",
    "Host 和 Client 的边界？Desktop Host 与 Electron main 的区别？",
    "新增只读查数据库工具，先改 core 还是扩展点？最小文件清单是什么？",
]

def diagnostic_html():
    out = ['<div class="quiz-card" id="diagnostic">',
           '<h2>开课前：5 题诊断</h2>',
           '<p class="hint">不查资料，写 1–2 句话即可；答案保存在本机浏览器，不会上传。</p>']
    for i, q in enumerate(DIAGNOSTIC, 1):
        out.append('<div class="q"><label for="diag-' + str(i) + '">' + str(i) + '. ' + html.escape(q) + '</label>')
        out.append('<textarea id="diag-' + str(i) + '" data-diag="' + str(i) + '" placeholder="你的回答…"></textarea></div>')
    out.append('<div class="row-actions">')
    out.append('<button class="btn primary" type="button" onclick="saveAnswers()">保存答案</button>')
    out.append('<button class="btn" type="button" onclick="exportAnswers()">复制 / 下载为 Markdown</button>')
    out.append('<span class="status" id="answer-status">未保存</span></div></div>')
    return "".join(out)

def assessment_card_html():
    return """
<div class="answer-card" id="answer-card">
  <h2>结课答题卡</h2>
  <p class="hint">先完成模块 1–3，再做下面 20 题和 C1–C4 中的 2 题。答案保存在本机浏览器，可导出为 Markdown 发给我评分。</p>
  <label for="final-answers"><strong>20 题答案</strong>（题号 + 你的回答）</label>
  <textarea class="big-answer" id="final-answers" data-big="final" placeholder="1. …&#10;2. …"></textarea>
  <label for="transfer-answers" style="display:block;margin-top:12px"><strong>迁移任务答案</strong>（写“选 C1/C2…”+ 方案）</label>
  <textarea class="big-answer" id="transfer-answers" data-big="transfer" placeholder="选 C1…&#10;…"></textarea>
  <div class="row-actions">
    <button class="btn primary" type="button" onclick="saveAnswers()">保存答案</button>
    <button class="btn" type="button" onclick="exportAnswers()">复制 / 下载为 Markdown</button>
    <span class="status" id="answer-status-2">未保存</span>
  </div>
</div>
"""

def section_html(num, section_id, title, subtitle, body, extra=""):
    return (
        '<section class="section" id="' + section_id + '" data-section="' + section_id + '">'
        '<div class="chapter"><div class="chapter-left"><div class="chapter-num">' + num + '</div>'
        '<div><h2>' + title + '</h2><p>' + subtitle + '</p></div></div>'
        '<button class="btn done-btn" type="button" data-done="' + section_id + '">标记完成</button></div>'
        + extra + '<div class="content">' + body + '</div></section>'
    )

SECTIONS = [
    ("overview", "00", "课程地图", "先读这一页，再按顺序进入三个模块", render_md("README.zh.md"), diagnostic_html()),
    ("m1", "01", "专业术语", "先把词用对：Turn、Step、Plugin、Service、Tool、Profile、Bundle、Patch", render_md("01-terminology.zh.md")),
    ("m2", "02", "项目架构", "从 CLI / Desktop 入口画到插件树、Host、Session 与工具执行", render_md("02-architecture.zh.md")),
    ("m3", "03", "代码实现", "沿真实文件追踪一次 turn，并做一个最小工具练习", render_md("03-code-implementation.zh.md")),
    ("m4", "04", "迁移能力测评", "术语 6 + 架构 7 + 代码 7；再选两个迁移任务", render_md("04-transfer-assessment.zh.md"), assessment_card_html()),
]
SECTIONS.append(("answers", "A", "参考答案", "建议做完题再展开", render_md("answer-key.zh.md")))

nav_html = []
for section_id, num, title, subtitle, body, *rest in SECTIONS:
    nav_html.append('<a href="#' + section_id + '" data-nav="' + section_id + '"><span class="nav-num">' + num + '</span><span>' + title + '</span></a>')
nav = "".join(nav_html)

sections = []
for section_id, num, title, subtitle, body, *rest in SECTIONS:
    extra = rest[0] if rest else ""
    if section_id == "answers":
        content = '<details class="answer-box"><summary>展开参考答案（学完再看）</summary>' + body + '</details>'
        sections.append(section_html(num, section_id, title, subtitle, content))
    else:
        sections.append(section_html(num, section_id, title, subtitle, body, extra))
sections_html = "".join(sections)

JS = """
(function () {
  var root = document.documentElement;
  var KEY = 'dsh-learning-answers-v1';
  var PROGRESS = 'dsh-learning-progress-v1';
  var THEME = 'dsh-learning-theme';

  function readStore(key, fallback) {
    try { var value = localStorage.getItem(key); return value ? JSON.parse(value) : fallback; }
    catch (error) { return fallback; }
  }
  function writeStore(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (error) { /* storage may be unavailable */ }
  }
  function allAnswers() {
    var data = readStore(KEY, {});
    document.querySelectorAll('[data-diag]').forEach(function (el) { data['diag-' + el.dataset.diag] = el.value; });
    document.querySelectorAll('[data-big]').forEach(function (el) { data['big-' + el.dataset.big] = el.value; });
    return data;
  }
  function restoreAnswers() {
    var data = readStore(KEY, {});
    document.querySelectorAll('[data-diag]').forEach(function (el) { el.value = data['diag-' + el.dataset.diag] || ''; });
    document.querySelectorAll('[data-big]').forEach(function (el) { el.value = data['big-' + el.dataset.big] || ''; });
  }
  function saveAnswers() {
    writeStore(KEY, allAnswers());
    document.querySelectorAll('#answer-status, #answer-status-2').forEach(function (el) { el.textContent = '已保存到本机 · ' + new Date().toLocaleTimeString(); });
  }
  function answerText() {
    var data = allAnswers();
    var lines = ['# DeepSeek Harness 学习答案', '', '## 诊断 5 题', ''];
    for (var i = 1; i <= 5; i += 1) {
      lines.push(i + '. ' + (document.querySelector('[data-diag="' + i + '"]').closest('.q').querySelector('label').textContent.replace(/^[0-9]+\\.\\s*/, '') || ''));
      lines.push('   ' + (data['diag-' + i] || '（未答）'), '');
    }
    lines.push('## 结课 20 题', '', data['big-final'] || '（未答）', '');
    lines.push('## 迁移任务', '', data['big-transfer'] || '（未答）', '');
    return lines.join('\\n');
  }
  function downloadMarkdown() {
    var text = answerText();
    var blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'dsh-learning-answers.md'; a.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function exportAnswers() {
    var text = answerText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { downloadMarkdown(); }).catch(function () { downloadMarkdown(); });
    } else { downloadMarkdown(); }
  }
  window.saveAnswers = saveAnswers;
  window.exportAnswers = exportAnswers;

  document.querySelectorAll('[data-diag], [data-big]').forEach(function (el) {
    el.addEventListener('input', function () { saveAnswers(); });
  });
  restoreAnswers();

  var progress = readStore(PROGRESS, {});
  function renderProgress() {
    var total = document.querySelectorAll('[data-done]').length;
    var done = 0;
    document.querySelectorAll('[data-done]').forEach(function (btn) {
      var id = btn.dataset.done;
      var isDone = !!progress[id];
      btn.classList.toggle('done', isDone);
      btn.textContent = isDone ? '已完成 ✓' : '标记完成';
      if (isDone) { done += 1; }
    });
    var pct = total ? Math.round((done / total) * 100) : 0;
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('progress-text').textContent = done + ' / ' + total + ' 节';
  }
  document.querySelectorAll('[data-done]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      progress[btn.dataset.done] = !progress[btn.dataset.done];
      writeStore(PROGRESS, progress);
      renderProgress();
    });
  });
  renderProgress();

  var theme = localStorage.getItem(THEME);
  if (theme === 'dark') { root.dataset.theme = 'dark'; }
  document.getElementById('theme-toggle').addEventListener('click', function () {
    root.dataset.theme = root.dataset.theme === 'dark' ? '' : 'dark';
    localStorage.setItem(THEME, root.dataset.theme || 'light');
    this.textContent = root.dataset.theme === 'dark' ? '浅色' : '深色';
  });
  if (root.dataset.theme === 'dark') { document.getElementById('theme-toggle').textContent = '浅色'; }

  document.getElementById('menu-toggle').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('open');
  });
  document.querySelectorAll('.nav a').forEach(function (a) {
    a.addEventListener('click', function () { document.getElementById('sidebar').classList.remove('open'); });
  });

  document.querySelectorAll('.content table').forEach(function (table) {
    var wrap = document.createElement('div');
    wrap.className = 'table-wrap';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  document.querySelectorAll('.content pre').forEach(function (pre) {
    var button = document.createElement('button');
    button.className = 'copy-code'; button.type = 'button'; button.textContent = '复制';
    button.addEventListener('click', function () {
      var code = pre.querySelector('code');
      if (!code) { return; }
      var text = code.innerText;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { button.textContent = '已复制'; setTimeout(function () { button.textContent = '复制'; }, 1200); });
      }
    });
    pre.appendChild(button);
  });

  var sections = Array.prototype.slice.call(document.querySelectorAll('section[data-section]'));
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) { return; }
        document.querySelectorAll('.nav a').forEach(function (a) { a.classList.toggle('active', a.dataset.nav === entry.target.id); });
      });
    }, { rootMargin: '-15% 0px -70% 0px', threshold: 0.01 });
    sections.forEach(function (section) { observer.observe(section); });
  }
  document.getElementById('print-btn').addEventListener('click', function () { window.print(); });
})();
"""

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DeepSeek Harness 学习与迁移课</title>
<meta name="description" content="DeepSeek Harness 三模块学习课：术语、架构、代码实现与迁移测评。">
<style>@@CSS@@</style>
</head>
<body>
<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand"><div class="brand-mark">DSH</div><div><strong>DeepSeek Harness</strong><small>学习与迁移课 · v1</small></div></div>
    <div class="nav-label">课程目录</div>
    <nav class="nav">@@NAV@@</nav>
    <div class="progress-box">
      <div class="progress-top"><span>学习进度</span><span id="progress-text">0 / 6 节</span></div>
      <div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div>
      <div class="side-actions"><button class="side-btn" id="theme-toggle" type="button">深色</button><button class="side-btn" id="print-btn" type="button">打印 / PDF</button></div>
    </div>
    <div class="progress-box" style="margin-top:12px">
      <div class="progress-top"><span>阅读约定</span></div>
      <div style="font-size:12px;color:var(--muted)">MD 给 Agent 与仓库维护；这个 HTML 是给你阅读、做题和导出的版本。答案只保存在本机浏览器。</div>
    </div>
  </aside>
  <main class="main">
    <div class="topbar"><button id="menu-toggle" type="button">目录</button><strong>DSH 学习课</strong><span style="font-size:12px;color:var(--muted)">HTML</span></div>
    <div class="wrap">
      <header class="hero">
        <div class="eyebrow">DeepSeek Harness · Linux port study guide</div>
        <h1>从术语到迁移：真正读懂 DSH</h1>
        <p>不背目录。先建立五个心智模型，再沿真实代码追踪一次 turn，最后用迁移任务检验你是否能把同样的判断用到新项目。</p>
        <div class="hero-meta"><span class="pill">3 个学习模块</span><span class="pill">5 题诊断</span><span class="pill">20 题结课</span><span class="pill">4 个迁移任务</span><span class="pill">答案本地保存</span></div>
      </header>
      <div class="stat-grid">
        <div class="stat"><strong>3</strong><span>学习模块</span></div>
        <div class="stat"><strong>5</strong><span>开课诊断题</span></div>
        <div class="stat"><strong>20</strong><span>结课问题</span></div>
        <div class="stat"><strong>4</strong><span>迁移任务（选 2）</span></div>
      </div>
      @@SECTIONS@@
      <div class="footer">由 DeepSeek Harness 学习课生成 · 自包含 HTML，无外部依赖 · 源文件在 <code>learning/</code> · 仓库：github.com/lsp725jk/deepseek-harness-linux</div>
    </div>
  </main>
</div>
<script>@@JS@@</script>
</body>
</html>
"""

out = HTML.replace("@@CSS@@", CSS).replace("@@NAV@@", nav).replace("@@SECTIONS@@", sections_html).replace("@@JS@@", JS)
target = LEARN / "index.html"
target.write_text(out, encoding="utf-8")
print("wrote", target, len(out), "bytes")
