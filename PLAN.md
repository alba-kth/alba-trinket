# alba-trinket — Python Tutor for Beginners

## What it is

A browser-based interactive Python teaching tool for beginner courses at KTH.
Inspired by colearn-ai.com (developed by an American professor using React + Skulpt + Claude API).

The goal is simpler than colearn-ai — no AI tutor, no login, no accounts.
Just a page where a teacher can present Python code examples with editable input files
that students can tinker with.

## Key design decisions

- **Skulpt** runs Python entirely in the browser — no server needed for code execution
- **CodeMirror** provides syntax highlighting and proper indentation in the code editor
- **Single HTML file** — a teacher creates one HTML file per exercise, no build step
- **Multiple file panes** — students can see and edit several text files simultaneously,
  which helps when learning file I/O with more than one file (a common point of confusion)
- **No saving, no accounts** — just open and tinker

## Tech stack

- Skulpt (Python in the browser via JavaScript) — loaded from CDN
- CodeMirror 5 (code editor with syntax highlighting) — loaded from CDN
- Bootstrap 5 (layout) — loaded from CDN
- A tiny Go file server (serve.go) for hosting — or any static web server

## Current state

- `tutor.html` — working prototype with:
  - Two editable file panes: `winter_sports.txt` and `cities.txt`
  - CodeMirror editor with Python highlighting, monokai theme, line numbers
  - Skulpt running Python in the browser — `open()` reads from the file panes
  - Output pane (dark background, errors in red)
  - Pre-filled with the "counting loop vs sentinel loop" exercise from colearn-ai
  - Run and Clear buttons
- `serve.go` — minimal Go static file server, listens on port 8081

## How to create a new exercise

Copy `tutor.html` and edit:
1. `<h2 id="exercise-title">` — exercise title
2. `<p id="exercise-description">` — description
3. File panes — each `<div class="file-pane">` is one file. Set `data-filename` to
   what `open()` will use in Python. Add or remove blocks freely.
4. The `<textarea id="code">` — the starting Python code

## How file I/O works (for future reference)

Skulpt's `open("filename", "r")` uses **`document.getElementById(filename)`** to find
the file content in the DOM. It does NOT use the `read` callback in `Sk.configure` for
this purpose (that callback is only for module imports).

Each file pane textarea must have an `id` attribute equal to the filename:
```html
<textarea id="winter_sports.txt" data-filename="winter_sports.txt">...</textarea>
```
When Python calls `open("winter_sports.txt")`, Skulpt finds the textarea by id and reads
its `.value`. The student has no idea it's not a real filesystem.

The `data-filename` attribute is used by our own JavaScript (in `runCode()`) to collect
file contents — it is separate from Skulpt's mechanism.

## Deployment

### Option A: KTH AFS/Apache (simplest, no server needed)
Copy files to `~/public_html/tutor/`. Apache serves them automatically.
```bash
cp tutor.html ~/public_html/tutor/
cp -r skulpt_files ~/public_html/tutor/
```
URL: https://www.csc.kth.se/~alba/tutor/tutor.html

Note: `skulpt_files/` contains local copies of Skulpt (skulpt.min.js, skulpt-stdlib.js).
tutor.html references them as `skulpt_files/skulpt.min.js` — no CDN needed.

### Option B: arepo.eecs.kth.se (own server)
Run `serve.go` on port 8081. Open port in ufw:
```bash
ufw allow from 130.237.0.0/16 to any port 8081   # KTH network only
```
Then run the server (from /home/alba/tutor):
```bash
go run serve.go
```
URL: http://arepo.eecs.kth.se:8081/tutor.html

## Current state (March 2026)

### Reference templates (do not edit for content)
- `tutor1_ref.html` — qtype1: counting loop vs sentinel loop (winter_sports.txt, cities.txt)
- `tutor2_ref.html` — qtype2: import exercise (helpers.py + names.txt + main code)
Both have template markers `<!-- BEGIN:field -->...<!-- END:field -->` for generate.py.

### Exercise generation system
- `generate.py` — reads a markdown exercise file, substitutes into the ref template,
  writes an HTML file next to the markdown source.
  Usage: `python3 generate.py samples/alba/tutor2/exercise.md`
- `samples/` — one subfolder per teacher, one subfolder per question type.
  Each exercise folder contains `exercise.md` (and optionally `feedback.yaml`).

### Markdown exercise format
```
---
type: qtype1 or qtype2
output: filename.html
---
# Title
## Description
(plain text; `backtick` → <code>)
## Files
### filename.py or filename.txt
(fenced code block)
## Main Code
(fenced code block)
```
`.py` files get CodeMirror syntax highlighting automatically (the ref JS handles it).

### Feedback (design, not yet implemented)
Optional `feedback.yaml` next to `exercise.md`. Planned format:
```yaml
checks:
  - type: output_equals
    expected: |
      Hello, world!
      42
    success: "You made it!"
  - type: output_contains
    text: "Hello"
    hint: "Make sure you call greet()."
  - type: file_contains
    file: names.txt
    text: "Dave"
    success: "You added a new name!"
```
Types planned: `output_equals`, `output_contains`, `output_matches`, `file_contains`.
If `feedback.yaml` is absent, no feedback is shown.

### Step debugger implementation
Uses `Sk.misceval.asyncToPromise(..., {'Sk.debug': debugHandler})`.
`debugHandler` returns a Promise that resolves when the user clicks Step.
`getSuspInfo` traverses to the INNERMOST `$lineno` in the suspension chain
(the outer layers stay suspended — e.g. the import statement in main while
helpers.py is running).

## Next steps / ideas

- [ ] Write a proper deploy script that syncs files in place (instead of rmtree+copytree)
      so AFS ACLs on public_html/src/kapitel_* are preserved across deploys.
      Currently: after each --copy-src deploy, must re-run fs sa on each kapitel dir.
- [ ] Download HTML button in teacher mode — needs CDN URLs for Skulpt/CodeMirror
      so the file is self-contained without local asset paths.
- [ ] Implement feedback.yaml checking in generate.py + runtime JS
- [ ] Try with real exercises from the colleague's course (samples/riese/)
- [ ] Authentication for save.php (currently open — consider KTH Kerberos .htaccess)

## Reference

- Skulpt docs: https://skulpt.org
- CodeMirror 5 docs: https://codemirror.net/5/
- colearn-ai.com — the inspiration (React + Skulpt + Claude API)
- The saved session in /home/alba/coLearn/coLearnReact.html shows a complete
  real exercise with student answers — useful reference for exercise design
