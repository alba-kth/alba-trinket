Python Tutor
============
Browser-based Python exercise tool using Skulpt (Python in the browser).

Quick start (local)
-------------------
1. Start a local web server in this folder:
     python3 -m http.server 8000

2. Open an exercise in your browser:
     http://localhost:8000/out/tutor1.html

Note: opening HTML files directly (file://) does not work — use the web server.

Generating exercises from markdown
-----------------------------------
Edit or create a markdown file in src/, then run:

    python3 generate.py src/kapitel_1/tutor1.md        # single file
    python3 generate.py src/kapitel_1/                  # whole folder

Output goes to out/ by default.

Deploying to a web server
--------------------------
Copy the assets once (skulpt_files/, codemirror_files/) to your web folder,
then deploy HTML with --asset-prefix "":

    python3 generate.py src/kapitel_1/ --out ~/public_html/tutor/ --asset-prefix ""

Screenshots (rgtutor1.jpg, rgtutor2.jpg, rgtutor4.jpg)
-------------------------------------------------------
Each screenshot shows the browser rendering (right) alongside the markdown
source with syntax highlighting (left), with arrows explaining:

  ####  — files placed side by side (flex row)
  ###   — files stacked vertically (full width)
  .py   — Python files get automatic syntax highlighting in the editor

License
-------
MIT License — see LICENSE
Third-party: CodeMirror (MIT), Skulpt (MIT) — see their LICENSE files.
