# alba-trinket

Browser-based interactive Python exercises for beginner courses at KTH.
Students edit and run Python code directly in the browser — no installation, no login.

**Live demo:** https://www.csc.kth.se/~alba/tutor/

---

## What it does

- Runs Python in the browser via [Skulpt](https://skulpt.org)
- Editable file panes — students can read and write files in Python (`open()`, `import`)
- Step debugger with line highlighting
- `input()` support with visual cue while waiting
- Teacher mode for creating and editing exercises live in the browser

---

## Project layout

```
src/                  Exercise source files (markdown)
  kapitel_1/
    trinket1.md
    ...
out/                  Generated HTML (git-ignored)
dist/                 Deploy build (git-ignored)
template.html         Single HTML template — all logic lives here
generate.py           Converts markdown exercises to HTML
deploy.py             Builds dist/ and deploys to AFS via rsync
server.py             Local dev server (static files + POST /save.php)
index.html            Exercise index page
skulpt_files/         Skulpt Python interpreter
codemirror_files/     CodeMirror editor
deploy.cfg.example    Config template — copy to deploy.cfg and edit
```

---

## Quick start (local)

```bash
python3 server.py
```

Open http://localhost:8000/out/trinket1.html

> Opening HTML files directly (`file://`) does not work — use the server.

---

## Writing exercises

Exercises are markdown files in `src/`. Example:

```markdown
---
type: qtype1
---
# Title of the exercise

## Description
Explain what the student should do. Use `backticks` for code.

## Files
### data.txt
```
line one
line two
```

#### helpers.py
```python
def greet(name):
    return f"Hello, {name}!"
```

## Main Code
```python
with open("data.txt") as f:
    for line in f:
        print(line.strip())
```
```

Rules:
- `###` filename — full-width file pane
- `####` filename — side-by-side with adjacent `####` panes
- `.py` files get syntax highlighting automatically

Generate HTML:

```bash
python3 generate.py src/kapitel_1/trinket1.md    # single file → out/
python3 generate.py src/kapitel_1/               # whole folder → out/
```

---

## Teacher mode

Open any exercise with `?mode=teacher`:

```
http://localhost:8000/out/trinket1.html?mode=teacher
```

A toolbar appears at the top with:
- **Load** — folder/filename dropdowns populated from `src/` (navigates on change)
- **Save As** — text inputs for folder and filename, writes back to `src/`
- **Generate iframe** — shows embed code for Canvas/LMS

The index page has a **Teacher mode** checkbox that appends `?mode=teacher` to all links.

---

## Deploying to AFS (KTH)

1. Copy `deploy.cfg.example` to `deploy.cfg` and fill in your settings:

   ```ini
   [deploy]
   ssh_host    = username@faculty-shell.sys.kth.se
   remote_path = public_html/alba-trinket
   save_token  = your-secret-token-here
   ```

2. Run:

   ```bash
   python3 deploy.py
   ```

   This will:
   - Update the save token in `template.html`
   - Generate all HTML into `dist/`
   - Copy assets and generate `save.php`
   - `rsync` everything to AFS
   - Set AFS ACLs (`fs sa`) so the web server can write to `src/`

> `deploy.cfg` is git-ignored — never commit it (it contains your secret token).

For quick fixes, edit directly on the server in teacher mode — changes are live immediately for all iframes.

---

## Manual deploy (without deploy.py)

```bash
python3 generate.py src/kapitel_1/ --out ~/public_html/alba-trinket/ --asset-prefix "" --copy-src
```

After first run or after adding a new folder, set AFS write permissions:
```bash
fs sa ~/public_html/alba-trinket/src/kapitel_1 cscwwwservice rliw
```

---

## License

MIT — see `LICENSE`
Third-party: [CodeMirror](https://codemirror.net) (MIT), [Skulpt](https://skulpt.org) (MIT)
