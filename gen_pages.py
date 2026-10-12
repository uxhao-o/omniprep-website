# -*- coding: utf-8 -*-
"""Generate Astro pages: EN from legacy static HTML, ZH/Changelog from Markdown."""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
OLD = ROOT.parent
PAGES = ROOT / "src" / "pages"
DOCS = OLD / "docs"

MD = None
import markdown as _md
MD = _md.Markdown(extensions=["tables", "fenced_code", "nl2br"])

def astro_escape(html: str) -> str:
    return html.replace("{", "&#123;").replace("}", "&#125;")

def fix_links(html: str) -> str:
    html = html.replace('src="assets/img/', 'src="/assets/img/')
    html = html.replace('src="assets/css/', 'src="/assets/css/')
    html = re.sub(r'href="(index|getting-started|documentation|about|changelog)\.html(#...)?"',
                  lambda m: 'href="/{}/"{}'.format(m.group(1), m.group(2) or ""), html)
    return html

def wrap(page: str, lang: str, title: str, desc: str, active: str, body: str) -> str:
    fm = ('---\n'
          f'import Layout from \'../layouts/Layout.astro\';\n' if lang == "en" else
          '---\n'
          f'import Layout from \'../../layouts/Layout.astro\';\n')
    fm = ("---\n"
          f"import Layout from '{'../' if lang=='en' else '../../'}layouts/Layout.astro';\n"
          "---\n")
    return (fm +
            f"<Layout lang=\"{lang}\" title=\"{title}\" description=\"{desc}\" active=\"{active}\">\n"
            + body + "\n</Layout>\n")

# ---------- 1) EN pages from legacy HTML ----------
EN_META = {
    "index": ("home", "OmniPrep — A Unified Pipeline for Accelerating Large-Scale Multimodal MRI Research Across the Lifespan"),
    "getting-started": ("start", "Getting Started — OmniPrep"),
    "documentation": ("docs", "Documentation — OmniPrep Parameter Reference"),
    "about": ("about", "About — OmniPrep"),
}
for name, (active, title) in EN_META.items():
    src = (OLD / f"{name}.html").read_text(encoding="utf-8")
    m = re.search(r"<main>(.*)</main>", src, re.S)
    body = fix_links(m.group(1))
    body = astro_escape(body)
    desc = "OmniPrep — unified multimodal MRI preprocessing and analysis pipeline."
    out = wrap(name, "en", title, desc, active, body)
    (PAGES / f"{name}.astro").write_text(out, encoding="utf-8")
    print("EN page:", name)

# ---------- 2) Markdown -> HTML helpers ----------
def preprocess_md(text: str) -> str:
    """Convert Material admonitions & tabs to plain HTML-friendly markdown."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^:::\s+(\w+)(?:\s+"?(.*?)"?)?\s*$', line)
        if m:
            kind, title = m.group(1), m.group(2) or kind_title(m.group(1))
            block, i = [], i + 1
            while i < len(lines) and lines[i].strip() != ":::":
                block.append(lines[i]); i += 1
            i += 1  # skip closing :::
            inner = MD.reset().convert("\n".join(block))
            out.append(f'<div class="callout {kind}"><p><strong>{title}.</strong> {inner}</p></div>')
            continue
        m = re.match(r'^===\s+"(.+?)"\s*$', line)
        if m:
            out.append(f'\n<h4>{m.group(1)}</h4>\n')
            i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
                out.append(lines[i][4:] if lines[i].startswith("    ") else lines[i])
                i += 1
            continue
        out.append(line); i += 1
    return "\n".join(out)

def kind_title(k):
    return {"note": "Note", "tip": "Tip", "warn": "Warning", "warning": "Warning", "info": "Info", "abstract": ""}.get(k, k.capitalize())

def md2html(text: str) -> str:
    return MD.reset().convert(preprocess_md(text))

def docs_shell(breadcrumb: str, h1: str, lead: str, content_html: str) -> str:
    return f'''<section class="page-hero">
  <div class="container">
    <div class="breadcrumb">{breadcrumb}</div>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>

<div class="container" style="max-width:900px;padding:48px 24px 80px">
  <article class="doc-content prose">
{content_html}
  </article>
</div>'''

# ---------- 3) ZH pages from docs/*.zh.md ----------
def zh_page(mdfile, slug, h1, lead, breadcrumb, title):
    text = (DOCS / mdfile).read_text(encoding="utf-8")
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.S)  # strip frontmatter
    if slug == "index":
        # Drop custom hero (replaced by handcrafted one below); keep from '## OmniPrep 概览'
        text = text[text.index("## OmniPrep 概览"):]
    html = md2html(text)
    html = html.replace('](assets/', '](/assets/')  # safety
    html = re.sub(r'href="([a-z-]+)(\.zh)?\.md(#[\w-]*)?"', lambda m: f'href="/zh/{m.group(1)}/{m.group(3) or ""}"', html)
    html = re.sub(r'href="([a-z-]+)\.md(#[\w-]*)?"', lambda m: f'href="/{m.group(1)}/{m.group(2) or ""}"', html)
    return html

def write_zh(slug, mdfile, h1, lead, active, title):
    if slug == "index":
        body = zh_index_body()
    else:
        crumb = f'<a href="/zh/">首页</a><span class="sep">/</span>{h1}'
        body = docs_shell(crumb, h1, lead, zh_page(mdfile, slug, h1, lead, crumb, title))
    body = astro_escape(body)
    out = wrap(slug, "zh", title, "OmniPrep 统一多模态 MRI 预处理与分析流程。", active, body)
    (PAGES / "zh" / f"{slug}.astro").write_text(out, encoding="utf-8")
    print("ZH page:", slug)

def zh_index_body():
    return '''<section class="hero">
  <div class="container">
    <span class="hero-badge"><span class="dot"></span> 多模态 · 可扩展 · 可复现</span>
    <h1>一个用于加速全生命周期<br />大规模<span class="grad">多模态 MRI 研究</span>的统一流程</h1>
    <p class="hero-sub">
      OmniPrep 在一个连贯的工作流中，对结构（sMRI）、功能（fMRI）和弥散（dMRI）MRI 数据
      进行标准化、预处理，并生成图集级和 ROI 级的衍生特征——可复现、可扩展、开箱即用。
    </p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/zh/getting-started/">快速开始</a>
      <a class="btn btn-ghost" href="/zh/documentation/">阅读文档</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">为什么选择 OmniPrep</span>
      <h2>OmniPrep 概览</h2>
      <p class="lead">一条命令，从原始 BIDS 数据到分析就绪的衍生数据，覆盖每一个 MRI 模态。</p>
    </div>
    <div class="grid grid-3">
      <div class="card"><div class="card-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg></div><h3>统一多模态</h3><p>结构、功能与弥散 MRI 预处理集成于单一连贯的工作流，无需拼接多个工具。</p></div>
      <div class="card"><div class="card-icon teal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></div><h3>基于 Nextflow</h3><p>可复现、容器化、可续跑。同一命令行即可从笔记本扩展到 HPC 集群与云端。</p></div>
      <div class="card"><div class="card-icon orange"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg></div><h3>图集与 ROI 衍生特征</h3><p>内置皮层图集、皮层下分割、形态学特征、ROI 时间序列、功能与结构连接组。</p></div>
      <div class="card"><div class="card-icon green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div><h3>内置质量控制</h3><p>每次运行自动生成 QC 报告、trace 和时间线——含头动 scrubbing 与 FD 帧检测。</p></div>
      <div class="card"><div class="card-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div><h3>年龄感知模板</h3><p>成人、儿童与婴儿队列，自动年龄检测并匹配 MNI 模板与畸变校正策略。</p></div>
      <div class="card"><div class="card-icon teal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4M4.2 4.2l2.8 2.8M17 17l2.8 2.8M4.2 19.8L7 17M17 7l2.8-2.8"/></svg></div><h3>GPU 加速</h3><p>自动调用可用 GPU，支持透明 CPU 回退与受监管的 GPU 守护进程。</p></div>
    </div>
  </div>
</section>

<section class="stats">
  <div class="container">
    <div class="stat"><div class="stat-num">3</div><div class="stat-label">MRI 模态</div></div>
    <div class="stat"><div class="stat-num">6<span class="unit">+</span></div><div class="stat-label">内置图集</div></div>
    <div class="stat"><div class="stat-num">60<span class="unit">+</span></div><div class="stat-label">配置选项</div></div>
    <div class="stat"><div class="stat-num">2</div><div class="stat-label">容器运行时</div></div>
  </div>
</section>

<section class="section soft">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">快速开始</span>
      <h2>三步运行</h2>
      <p class="lead">从原始 BIDS 数据到衍生数据，几分钟完成。</p>
    </div>
    <div class="grid grid-2" style="align-items:start">
      <div>
        <ol class="steps">
          <li>
            <h4>拉取容器镜像</h4>
            <p>从 Docker Hub 获取预构建的 OmniPrep 镜像。</p>
            <div class="code-block"><div class="cb-head"><span class="cb-label">bash</span><button class="copy-btn">复制</button></div><pre><code>docker pull uxhao/omniprep:latest</code></pre></div>
          </li>
          <li>
            <h4>准备 BIDS 数据与许可证</h4>
            <p>指向你的 BIDS 目录和 FreeSurfer 许可证文件。</p>
          </li>
          <li>
            <h4>启动流程</h4>
            <p>以所需模态运行工作流。</p>
            <div class="code-block"><div class="cb-head"><span class="cb-label">bash</span><button class="copy-btn">复制</button></div><pre><code>docker run -it --rm --gpus all \\
  -v /path/to/bids:/data \\
  -v /path/to/output:/out \\
  -v /path/to/license.txt:/license.txt \\
  uxhao/omniprep:latest /data /out participant \\
  --fs_license_file /license.txt \\
  --tasks "anat bold dwi"</code></pre></div>
          </li>
        </ol>
      </div>
      <div>
        <div class="card" style="box-shadow:var(--shadow-md)">
          <h3 style="display:flex;align-items:center;gap:9px">产出内容</h3>
          <p>OmniPrep 将结果写入 <code style="font-family:var(--font-mono)">output_dir/derivatives/omniprep</code>：</p>
          <div class="pill-row">
            <span class="pill hl">Recon/</span><span class="pill hl">BOLD/</span><span class="pill hl">DWI/</span><span class="pill hl">QC/</span>
            <span class="pill">report.html</span><span class="pill">timeline.html</span>
          </div>
          <ul style="margin-top:16px;padding-left:20px;color:var(--muted);font-size:.93rem">
            <li>FreeSurfer 重建与形态学</li>
            <li>去噪 BOLD + 体素/ROI 指标</li>
            <li>纤维追踪与连接组</li>
            <li>自动化 QC 报告</li>
          </ul>
          <a class="btn btn-primary" style="margin-top:16px" href="/zh/getting-started/">查看完整指南 →</a>
        </div>
      </div>
    </div>
  </div>
</section>'''

write_zh("index", "index.zh.md", "首页", "", "home", "OmniPrep — 一个用于加速全生命周期大规模多模态 MRI 研究的统一流程")
write_zh("getting-started", "getting-started.zh.md", "快速开始",
         "安装 OmniPrep、获取 FreeSurfer 许可证，并在几分钟内完成你的第一个 BIDS 数据集预处理。",
         "start", "快速开始 — OmniPrep")
write_zh("documentation", "documentation.zh.md", "参数参考",
         "OmniPrep 完整命令行接口，按类别组织。每个选项都标注了类型、默认值与行为。",
         "docs", "文档 — OmniPrep 参数参考")
write_zh("about", "about.zh.md", "关于 OmniPrep",
         "一个用于加速全生命周期大规模多模态 MRI 研究的统一流程。",
         "about", "关于 — OmniPrep")

# ---------- 4) Changelog pages (EN + ZH) ----------
def strip_fm(text): return re.sub(r"^---.*?---\s*", "", text, flags=re.S)

en_cl = (DOCS / "changelog.md").read_text(encoding="utf-8")
en_html = md2html(strip_fm(en_cl))
en_html = re.sub(r'href="https://github\.com/uxhao/OmniPrep/releases"\)', 'href="https://github.com/uxhao/OmniPrep/releases")', en_html)
body = docs_shell('<a href="/">Home</a><span class="sep">/</span>Changelog', 'Changelog',
                  'All notable changes to OmniPrep are documented here.', en_html)
(PAGES / "changelog.astro").write_text(
    wrap("changelog", "en", "Changelog — OmniPrep", "OmniPrep release notes and version history.", "log",
         astro_escape(body)), encoding="utf-8")
print("EN page: changelog")

zh_cl = (DOCS / "changelog.zh.md").read_text(encoding="utf-8")
zh_html = md2html(strip_fm(zh_cl))
body = docs_shell('<a href="/zh/">首页</a><span class="sep">/</span>更新日志', '更新日志',
                  'OmniPrep 的所有重要变更都记录于此。', zh_html)
(PAGES / "zh" / "changelog.astro").write_text(
    wrap("changelog", "zh", "更新日志 — OmniPrep", "OmniPrep 发布说明与版本历史。", "log",
         astro_escape(body)), encoding="utf-8")
print("ZH page: changelog")

# ---------- 5) Search pages (Pagefind UI) ----------
def search_page(lang):
    zh = lang == "zh"
    prefix = "/zh" if zh else ""
    body = f'''<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="{prefix}/">{'首页' if zh else 'Home'}</a><span class="sep">/</span>{'搜索' if zh else 'Search'}</div>
    <h1>{'搜索文档' if zh else 'Search the docs'}</h1>
    <p class="lead">{'输入关键词，搜索全部 OmniPrep 文档。' if zh else 'Type keywords to search the full OmniPrep documentation.'}</p>
  </div>
</section>
<div class="container" style="max-width:860px;padding:40px 24px 80px">
  <div id="search"></div>
</div>
<script>
  import {{ PagefindUI }} from '@pagefind/default-ui';
  import '@pagefind/default-ui/css/ui.css';
  new PagefindUI({{ element: '#search', showSubResults: true }});
</script>'''
    return wrap("search", lang, ("搜索 — OmniPrep" if zh else "Search — OmniPrep"),
                "Search the OmniPrep documentation.", "", astro_escape(body))

(PAGES / "search.astro").write_text(search_page("en"), encoding="utf-8")
(PAGES / "zh" / "search.astro").write_text(search_page("zh"), encoding="utf-8")
print("Search pages done")
