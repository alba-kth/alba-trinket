#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Alexander Baltatzis <alba@kth.se>
"""
generate.py — generate a tutor exercise HTML from a markdown definition.

Usage:
    python3 generate.py <exercise.md> [--out <output_dir>] [--asset-prefix <prefix>]
    python3 generate.py <folder/>    [--out <output_dir>] [--copy-src]  — processes all .md files in folder

Default output directory: out/  (next to generate.py)
Default asset prefix:     ../   (assets one level up from out/)

For web deployment where HTML and assets are in the same directory:
    python3 generate.py src/kapitel_1/ --out ~/public_html/tutor/ --asset-prefix ""

Output filename is derived from the markdown filename:
    src/alba/tutor2.md  →  out/tutor2.html

Mandatory sections in the markdown:
    # Title
    ## Description
    ## Main Code

Optional section:
    ## Files
      ### filename   — full-width row
      #### filename  — side-by-side with adjacent #### files

If ## Files is absent or has no file blocks, the file section is omitted.
"""

import sys
import re
import os
import shutil
import html as htmllib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SCRIPT_DIR, 'template.html')
DEFAULT_OUT = os.path.join(SCRIPT_DIR, 'out')


def parse_args(argv):
    args = argv[1:]
    out_dir = DEFAULT_OUT
    asset_prefix = '../'
    md_path = None
    copy_src = False
    i = 0
    while i < len(args):
        if args[i] == '--out':
            i += 1
            if i >= len(args):
                sys.exit('Error: --out requires a directory argument')
            out_dir = args[i]
        elif args[i] == '--asset-prefix':
            i += 1
            if i >= len(args):
                sys.exit('Error: --asset-prefix requires an argument')
            asset_prefix = args[i]
        elif args[i] == '--copy-src':
            copy_src = True
        else:
            md_path = args[i]
        i += 1
    return md_path, out_dir, asset_prefix, copy_src


def parse_frontmatter(text):
    """Parse simple key: value YAML frontmatter. Returns (meta_dict, body)."""
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    rest = text[end + 5:]
    meta = {}
    for line in text[4:end].strip().split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            meta[k.strip()] = v.strip()
    return meta, rest


def parse_code_block(text):
    """Return content of the first fenced code block, or stripped plain text.
    Tabs are expanded to 4 spaces to avoid Python mixed-indentation errors."""
    m = re.search(r'```[^\n]*\n(.*?)```', text, re.DOTALL)
    content = m.group(1) if m else text.strip()
    return content.expandtabs(4)


def md_to_html(text):
    """Minimal markdown → HTML: escape, then `code` → <code>."""
    text = htmllib.escape(text.strip(), quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def parse_file_rows(files_section_text):
    """Parse ### and #### file blocks into rows.

    ### filename  → full-width row (its own div.file-panes)
    #### filename → side-by-side with adjacent #### files (shared div.file-panes)

    Returns a list of rows. Each row is a list of (filename, content) tuples.
    """
    rows = []
    current_group = []

    pattern = r'^(#{3,4}) (.+?)\s*\n(.*?)(?=^#{3,4} |\Z)'
    for m in re.finditer(pattern, files_section_text, re.MULTILINE | re.DOTALL):
        level = len(m.group(1))
        filename = m.group(2).strip()
        content = parse_code_block(m.group(3))

        if level == 3:  # ### = full-width row
            if current_group:
                rows.append(current_group)
                current_group = []
            rows.append([(filename, content)])
        else:           # #### = accumulate into side-by-side group
            current_group.append((filename, content))

    if current_group:
        rows.append(current_group)

    return rows


def parse_exercise(md_text):
    """Parse a markdown exercise file. Returns a dict."""
    _, body = parse_frontmatter(md_text)

    m = re.search(r'^# (.+)$', body, re.MULTILINE)
    title = m.group(1).strip() if m else None

    m = re.search(r'^## Description\s*\n(.*?)(?=^## |\Z)', body, re.MULTILINE | re.DOTALL)
    description = m.group(1).strip() if m else None

    file_rows = []
    m = re.search(r'^## Files\s*\n(.*?)(?=^## |\Z)', body, re.MULTILINE | re.DOTALL)
    if m:
        file_rows = parse_file_rows(m.group(1))

    m = re.search(r'^## Main Code\s*\n(.*?)(?=^## |\Z)', body, re.MULTILINE | re.DOTALL)
    main_code = parse_code_block(m.group(1)) if m else None

    return {
        'title': title,
        'description': description,
        'file_rows': file_rows,
        'main_code': main_code,
    }


def validate(exercise):
    errors = []
    for field in ('title', 'description', 'main_code'):
        if not exercise.get(field):
            errors.append(f'Missing: {field}')
    return errors


def make_file_pane(filename, content):
    rows = max(8, min(20, content.count('\n') + 2))
    esc_name = htmllib.escape(filename, quote=True)
    esc_content = htmllib.escape(content, quote=False)
    return (
        f'    <div class="file-pane">\n'
        f'      <label><code>{esc_name}</code></label>\n'
        f'      <textarea rows="{rows}" id="{esc_name}" data-filename="{esc_name}">'
        f'{esc_content}</textarea>\n'
        f'    </div>'
    )


def make_file_row_html(row):
    panes = '\n\n'.join(make_file_pane(fn, c) for fn, c in row)
    return f'  <div class="file-panes">\n\n{panes}\n\n  </div>'


def make_file_rows_html(file_rows):
    if not file_rows:
        return ''
    rows_html = '\n\n'.join(make_file_row_html(row) for row in file_rows)
    return (
        '  <h5>Files</h5>\n'
        '  <p class="muted small">You can edit these files. '
        'Your Python code can open() or import them by name.</p>\n\n'
        + rows_html + '\n'
    )


def substitute(html, marker, new_content):
    """Replace <!-- BEGIN:marker -->...<!-- END:marker --> with new content."""
    pattern = rf'<!-- BEGIN:{re.escape(marker)} -->.*?<!-- END:{re.escape(marker)} -->'
    replacement = f'<!-- BEGIN:{marker} -->{new_content}<!-- END:{marker} -->'
    result, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if n == 0:
        print(f'  Warning: marker "{marker}" not found in template', file=sys.stderr)
    return result


def generate_html(exercise, template_path, asset_prefix='../'):
    with open(template_path) as f:
        html = f.read()

    base_tag = f'<base href="{asset_prefix}">' if asset_prefix else ''
    html = substitute(html, 'base', base_tag)

    html = substitute(html, 'title',
        f'<h2 id="exercise-title">{htmllib.escape(exercise["title"], quote=False)}</h2>')

    desc_html = md_to_html(exercise['description'])
    html = substitute(html, 'description',
        f'<p class="muted" id="exercise-description">\n    {desc_html}\n  </p>')

    html = substitute(html, 'file-rows', make_file_rows_html(exercise['file_rows']))

    esc_code = htmllib.escape(exercise['main_code'], quote=False)
    html = substitute(html, 'code', f'<textarea id="code">{esc_code}\n</textarea>')

    return html


def generate_one(md_path, out_dir, asset_prefix):
    with open(md_path) as f:
        md_text = f.read()

    exercise = parse_exercise(md_text)
    errors = validate(exercise)
    if errors:
        print(f'{md_path}: errors:')
        for e in errors:
            print(f'  - {e}')
        return False

    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(md_path))[0]
    out_path = os.path.join(out_dir, stem + '.html')

    feedback_path = os.path.join(os.path.dirname(os.path.abspath(md_path)), 'feedback.yaml')
    if os.path.isfile(feedback_path):
        print(f'Note: feedback.yaml found next to {os.path.basename(md_path)} but not yet applied.')

    html = generate_html(exercise, TEMPLATE, asset_prefix)

    with open(out_path, 'w') as f:
        f.write(html)

    print(f'Generated: {out_path}')
    return True


def copy_src_dir(out_dir):
    src = os.path.join(SCRIPT_DIR, 'src')
    dest = os.path.join(out_dir, 'src')
    if not os.path.isdir(src):
        print(f'Warning: src/ not found, skipping --copy-src', file=sys.stderr)
        return
    n = 0
    for dirpath, dirnames, filenames in os.walk(src):
        # Skip backup files
        filenames = [f for f in filenames if not f.endswith('~')]
        rel = os.path.relpath(dirpath, src)
        dest_dir = os.path.join(dest, rel) if rel != '.' else dest
        os.makedirs(dest_dir, exist_ok=True)
        for f in filenames:
            shutil.copy2(os.path.join(dirpath, f), os.path.join(dest_dir, f))
            n += 1
    print(f'Synced: src/ → {dest} ({n} files)')


def main():
    md_path, out_dir, asset_prefix, copy_src = parse_args(sys.argv)

    if not md_path:
        sys.exit(__doc__)

    if not os.path.isfile(TEMPLATE):
        sys.exit(f'Error: template not found: {TEMPLATE}')

    if os.path.isdir(md_path):
        md_files = sorted(
            os.path.join(md_path, f)
            for f in os.listdir(md_path)
            if f.endswith('.md') and not f.endswith('~')
        )
        subdirs = sorted(
            d for d in os.listdir(md_path)
            if os.path.isdir(os.path.join(md_path, d))
        )
        if subdirs and not md_files:
            # Parent directory with subdirectories — generate each into out/<folder>/
            ok = True
            for d in subdirs:
                sub_md = sorted(
                    os.path.join(md_path, d, f)
                    for f in os.listdir(os.path.join(md_path, d))
                    if f.endswith('.md') and not f.endswith('~')
                )
                if not sub_md:
                    continue
                sub_out = os.path.join(out_dir, d)
                sub_prefix = asset_prefix if asset_prefix != '../' else '../'
                ok = all(generate_one(p, sub_out, sub_prefix) for p in sub_md) and ok
            if not ok:
                sys.exit(1)
        elif md_files:
            ok = all(generate_one(p, out_dir, asset_prefix) for p in md_files)
            if not ok:
                sys.exit(1)
        else:
            sys.exit(f'No .md files found in {md_path}')
    elif os.path.isfile(md_path):
        if not generate_one(md_path, out_dir, asset_prefix):
            sys.exit(1)
    else:
        sys.exit(f'Error: not found: {md_path}')

    if copy_src:
        copy_src_dir(out_dir)


if __name__ == '__main__':
    main()
