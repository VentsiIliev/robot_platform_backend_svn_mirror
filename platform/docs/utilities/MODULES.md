# Module reference: `.`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [run_coverage.py](#run_coveragepy)
- [serve_docs.py](#serve_docspy)

## `run_coverage.py`

Source: [run_coverage.py](../../run_coverage.py).

Run the test suite with coverage and print a report. Usage: python run_coverage.y_pixels # text report in terminal python run_coverage.y_pixels --html # also open htmlcov/index.html python run_coverage.y_pixels --missing # show missing line numbers python run_coverage.y_pixels --fail-under 50 # exit 1 if below 50 % Requirements: pip install coverage (or: .venv/bin/pip install coverage)

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `os`, `pathlib`, `subprocess`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parent
```

### `main`

```python
def main() -> None
```

## `serve_docs.py`

Source: [serve_docs.py](../../serve_docs.py).

Serve the docs/ directory as a website in your browser. Usage: python serve_docs.y_pixels # opens http://localhost:7000 python serve_docs.y_pixels --port 8080 # custom port python serve_docs.y_pixels --no-open # don't auto-open browser No external dependencies — stdlib only.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `html`, `http.server`, `os`, `pathlib`, `re`, `sys`, `threading`, `urllib.parse`, `webbrowser`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / 'docs'
TITLE = 'Robot App Platform — Docs'
CSS = '\n:root {\n  --bg:        #0d1117;\n  --bg-card:   #161b22;\n  --bg-nav:    #0d1117;\n  --border:    #30363d;\n  --text:      #e6edf3;\n  --text-dim:  #8b949e;\n  --accent:    #58a6ff;\n  --accent2:   #3fb950;\n  --code-bg:   #1f2428;\n  --nav-w:     260px;\n}\n\n* { box-sizing: border-box; margin: 0; padding: 0; }\n\nbody {\n  font-family: -apple-vision_service, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;\n  background: var(--bg);\n  color: var(--text);\n  display: flex;\n  min-height: 100vh;\n  font-size: 15px;\n  line-height: 1.65;\n}\n\n/* ── Sidebar ── */\n#sidebar {\n  width: var(--nav-w);\n  min-width: var(--nav-w);\n  background: var(--bg-nav);\n  border-right: 1px solid var(--border);\n  overflow-y: auto;\n  position: sticky;\n  top: 0;\n  height: 100vh;\n  padding: 16px 0 32px;\n}\n\n#sidebar h1 {\n  font-size: 13px;\n  font-weight: 600;\n  letter-spacing: .04em;\n  text-transform: uppercase;\n  color: var(--text-dim);\n  padding: 0 16px 12px;\n  border-bottom: 1px solid var(--border);\n  margin-bottom: 12px;\n}\n\nul.nav-root, ul.nav-root ul { list-style: none; padding: 0; }\n\n.nav-dir { padding: 0; }\n.nav-dir-label {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  width: 100%;\n  background: none;\n  border: none;\n  cursor: pointer;\n  font-size: 12px;\n  font-weight: 600;\n  letter-spacing: .04em;\n  text-transform: uppercase;\n  color: var(--text-dim);\n  padding: 8px 16px 3px;\n  text-align: left;\n}\n.nav-dir-label::before {\n  content: \'▾\';\n  font-size: 11px;\n  line-height: 1;\n  flex-shrink: 0;\n  transition: transform .15s ease;\n  display: inline-block;\n}\n.nav-dir-label:hover { color: var(--text); }\n.nav-dir.collapsed > .nav-dir-label::before { transform: rotate(-90deg); }\n.nav-dir.collapsed > ul { display: none; }\n\n/* Indentation with vertical guide line for nested levels */\n.nav-dir ul {\n  padding-left: 0;\n  margin-left: 20px;\n  border-left: 1px solid var(--border);\n}\n\n.nav-file a {\n  display: block;\n  padding: 3px 10px;\n  color: var(--text-dim);\n  text-decoration: none;\n  font-size: 13.5px;\n  border-radius: 4px;\n  margin: 1px 4px;\n  transition: background .12s, color .12s;\n}\n.nav-file a:hover  { color: var(--text); background: #1c2128; }\n.nav-file.active a { color: var(--accent); background: #1c2128; font-weight: 500; }\n\n/* ── Main content ── */\n#content {\n  flex: 1;\n  max-width: 900px;\n  padding: 40px 48px 80px;\n  overflow-x: hidden;\n}\n\n/* ── Typography ── */\nh1, h2, h3, h4, h5, h6 {\n  color: var(--text);\n  font-weight: 600;\n  margin: 1.6em 0 .5em;\n  line-height: 1.25;\n}\nh1 { font-size: 2em;   border-bottom: 1px solid var(--border); padding-bottom: .3em; }\nh2 { font-size: 1.5em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }\nh3 { font-size: 1.25em; }\nh4 { font-size: 1em; }\n\np { margin: .75em 0; color: var(--text); }\na { color: var(--accent); text-decoration: none; }\na:hover { text-decoration: underline; }\nhr { border: none; border-top: 1px solid var(--border); margin: 1.5em 0; }\n\nstrong { font-weight: 600; }\ndel { color: var(--text-dim); }\n\n/* ── Code ── */\ncode {\n  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;\n  font-size: .875em;\n  background: var(--code-bg);\n  padding: .15em .4em;\n  border-radius: 4px;\n  color: #f78166;\n}\npre {\n  background: var(--code-bg);\n  border: 1px solid var(--border);\n  border-radius: 8px;\n  padding: 16px;\n  overflow-x: auto;\n  margin: 1em 0;\n}\npre code {\n  color: #e6edf3;\n  background: none;\n  padding: 0;\n  font-size: .875em;\n}\n\n/* ── Tables ── */\ntable {\n  width: 100%;\n  border-collapse: collapse;\n  margin: 1em 0;\n  font-size: .9em;\n}\nthead { background: #1c2128; }\nth, td {\n  padding: 8px 12px;\n  border: 1px solid var(--border);\n  text-align: left;\n  vertical-align: top;\n}\nth { font-weight: 600; color: var(--text); }\ntd code { font-size: .8em; }\ntr:nth-child(even) { background: #0f1318; }\n\n/* ── Lists ── */\nul, ol { padding-left: 1.5em; margin: .5em 0; }\nli { margin: .25em 0; }\n\n/* ── Blockquote ── */\nblockquote {\n  border-left: 3px solid var(--accent);\n  margin: 1em 0;\n  padding: .5em 1em;\n  color: var(--text-dim);\n  background: #1c2128;\n  border-radius: 0 6px 6px 0;\n}\n\n/* ── Collapsible content sections ── */\n.collapsible-h {\n  cursor: pointer;\n  user-select: none;\n  display: flex;\n  align-items: center;\n  gap: 8px;\n}\n.collapsible-h::before {\n  content: \'▾\';\n  font-size: 0.65em;\n  opacity: 0.45;\n  flex-shrink: 0;\n  transition: transform .15s ease;\n  display: inline-block;\n}\n.collapsible-h.section-closed::before { transform: rotate(-90deg); }\n.collapsible-h:hover::before { opacity: 0.9; }\n.section-body.section-hidden { display: none; }\n\n/* ── Breadcrumb ── */\n#breadcrumb {\n  font-size: 12px;\n  color: var(--text-dim);\n  margin-bottom: 20px;\n  display: flex;\n  gap: 6px;\n  align-items: center;\n  flex-wrap: wrap;\n}\n#breadcrumb a { color: var(--text-dim); }\n#breadcrumb a:hover { color: var(--accent); }\n#breadcrumb .sep { color: var(--border); }\n\n/* ── Search box ── */\n#search-wrap { padding: 8px 12px 12px; }\n#search {\n  width: 100%;\n  background: #1c2128;\n  border: 1px solid var(--border);\n  border-radius: 6px;\n  color: var(--text);\n  font-size: 13px;\n  padding: 6px 10px;\n  outline: none;\n}\n#search::placeholder { color: var(--text-dim); }\n#search:focus { border-color: var(--accent); }\n\n/* hide non-matching nav items */\n.nav-file.search-hidden { display: none; }\n'
JS = "\n(function() {\n  // Default: everything collapsed. localStorage stores which dirs are OPEN.\n  var STORAGE_KEY = 'nav-open-v1';\n\n  function getOpen() {\n    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }\n    catch(e) { return []; }\n  }\n  function setOpen(keys) {\n    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(keys)); } catch(e) {}\n  }\n\n  // Collect ancestor dir keys of the active nav item — always kept open\n  var ancestorKeys = [];\n  var active = document.querySelector('.nav-file.active');\n  if (active) {\n    var el = active.parentElement;\n    while (el) {\n      if (el.classList && el.classList.contains('nav-dir') && el.dataset.key) {\n        ancestorKeys.push(el.dataset.key);\n      }\n      el = el.parentElement;\n    }\n  }\n\n  // Start all dirs collapsed, then open the ones in storage + ancestors\n  var openKeys = getOpen();\n  document.querySelectorAll('.nav-dir').forEach(function(dir) {\n    var key = dir.dataset.key;\n    var shouldOpen = openKeys.indexOf(key) !== -1 || ancestorKeys.indexOf(key) !== -1;\n    if (!shouldOpen) {\n      dir.classList.add('collapsed');\n    }\n  });\n\n  // Toggle on label click\n  document.querySelectorAll('.nav-dir-label').forEach(function(btn) {\n    btn.addEventListener('click', function() {\n      var dir = btn.closest('.nav-dir');\n      if (!dir) return;\n      dir.classList.toggle('collapsed');\n      var key = dir.dataset.key;\n      var stored = getOpen();\n      if (!dir.classList.contains('collapsed')) {\n        // now open — add to stored\n        if (stored.indexOf(key) === -1) stored.push(key);\n      } else {\n        // now closed — remove from stored\n        stored = stored.filter(function(k) { return k !== key; });\n      }\n      setOpen(stored);\n    });\n  });\n\n  // Live search filter\n  var search = document.getElementById('search');\n  if (search) {\n    search.addEventListener('input', function() {\n      var q = this.value.toLowerCase().trim();\n      document.querySelectorAll('.nav-file').forEach(function(li) {\n        if (!q || li.textContent.toLowerCase().includes(q)) {\n          li.classList.remove('search-hidden');\n        } else {\n          li.classList.add('search-hidden');\n        }\n      });\n      // While searching: expand all dirs with matches; on clear, restore state\n      document.querySelectorAll('.nav-dir').forEach(function(dir) {\n        var visible = dir.querySelectorAll('.nav-file:not(.search-hidden)').length;\n        if (q) {\n          dir.style.display = visible ? '' : 'none';\n          if (visible) dir.classList.remove('collapsed');\n        } else {\n          dir.style.display = '';\n          var stored = getOpen();\n          var key = dir.dataset.key;\n          var shouldOpen = stored.indexOf(key) !== -1 || ancestorKeys.indexOf(key) !== -1;\n          dir.classList.toggle('collapsed', !shouldOpen);\n        }\n      });\n    });\n  }\n\n  // Scroll active item into view\n  if (active) active.scrollIntoView({ block: 'center', behavior: 'instant' });\n})();\n\n// ── Collapsible content sections (h2 level) ───────────────────────────────\n// Default: all collapsed. localStorage stores which sections are OPEN.\n(function() {\n  var PAGE_KEY = 'sections-open:' + location.pathname;\n\n  function getOpen() {\n    try { return JSON.parse(localStorage.getItem(PAGE_KEY) || '[]'); }\n    catch(e) { return []; }\n  }\n  function saveOpen(ids) {\n    try { localStorage.setItem(PAGE_KEY, JSON.stringify(ids)); } catch(e) {}\n  }\n\n  var content = document.getElementById('content');\n  if (!content) return;\n\n  var headings = Array.from(content.querySelectorAll('h2'));\n  var openIds = getOpen();\n\n  headings.forEach(function(h) {\n    // Collect all siblings after h until the next h2\n    var body = [];\n    var next = h.nextElementSibling;\n    while (next && next.tagName !== 'H2') {\n      body.push(next);\n      next = next.nextElementSibling;\n    }\n    if (body.length === 0) return;\n\n    // Wrap body in a div\n    var wrapper = document.createElement('div');\n    wrapper.className = 'section-body';\n    h.parentNode.insertBefore(wrapper, body[0]);\n    body.forEach(function(el) { wrapper.appendChild(el); });\n\n    // Ensure heading has a stable id\n    if (!h.id) h.id = 'section-' + h.textContent.trim().toLowerCase().replace(/\\s+/g, '-');\n    var id = h.id;\n\n    h.classList.add('collapsible-h');\n\n    // Default collapsed — only open if stored as open\n    if (openIds.indexOf(id) === -1) {\n      wrapper.classList.add('section-hidden');\n      h.classList.add('section-closed');\n    }\n\n    // Toggle on click\n    h.addEventListener('click', function() {\n      var nowHidden = wrapper.classList.toggle('section-hidden');\n      h.classList.toggle('section-closed', nowHidden);\n      var stored = getOpen();\n      if (!nowHidden) {\n        if (stored.indexOf(id) === -1) stored.push(id);\n      } else {\n        stored = stored.filter(function(k) { return k !== id; });\n      }\n      saveOpen(stored);\n    });\n  });\n})();\n"
```

### `md_to_html`

```python
def md_to_html(text: str) -> str
```

Convert a Markdown string to an HTML fragment.

### `_label`

```python
def _label(path: Path) -> str
```

Human-readable label for a path segment.

### `build_nav`

```python
def build_nav(base: Path, current_path: str) -> str
```

Recursively build an HTML navigation tree for the sidebar.

### `render_page`

```python
def render_page(md_path: Path, current_url: str) -> bytes
```

Render a .md file as a full HTML page.

### `render_index`

```python
def render_index() -> bytes
```

Render the docs root index (list of top-level sections).

### `DocsHandler`

```python
class DocsHandler(BaseHTTPRequestHandler):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def log_message(self, fmt, *args)
```

```python
def do_GET(self)
```

### `main`

```python
def main()
```
