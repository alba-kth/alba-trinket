#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Alexander Baltatzis <alba@kth.se>
"""
server.py — local development server for alba-trinket.

Serves static files from the project root and handles POST /save.php
to write markdown exercises to src/.

Usage:
    python3 server.py [port]   (default port: 8000)

Then open:
    http://localhost:8000/out/trinket1.html?mode=teacher
"""

import configparser
import http.server
import json
import os
import re
import sys
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT   = os.path.join(SCRIPT_DIR, 'src')


def load_token():
    cfg_path = os.path.join(SCRIPT_DIR, 'deploy.cfg')
    if os.path.exists(cfg_path):
        cfg = configparser.ConfigParser()
        cfg.read(cfg_path)
        return cfg.get('deploy', 'save_token', fallback=None)
    # Fallback: read from template.html
    tpl = os.path.join(SCRIPT_DIR, 'template.html')
    if os.path.exists(tpl):
        with open(tpl) as f:
            m = re.search(r"const SAVE_TOKEN = '([^']+)'", f.read())
            if m:
                return m.group(1)
    return None


SAVE_TOKEN = load_token()


def handle_save(body_bytes):
    params = dict(urllib.parse.parse_qsl(body_bytes.decode()))
    token    = params.get('token', '')
    folder   = params.get('folder', '').strip()
    filename = params.get('filename', '').strip()
    content  = params.get('content', '')

    if SAVE_TOKEN and token != SAVE_TOKEN:
        return 403, {'error': 'Forbidden'}

    if not re.match(r'^[a-zA-Z0-9_-]+\.md$', filename):
        return 400, {'error': 'Invalid filename — must match [a-zA-Z0-9_-].md'}

    if not re.match(r'^[a-zA-Z0-9_-]+$', folder):
        return 400, {'error': 'Invalid folder name'}

    target_dir = os.path.realpath(os.path.join(SRC_ROOT, folder))
    if not target_dir.startswith(os.path.realpath(SRC_ROOT) + os.sep):
        return 400, {'error': 'Folder not found or outside src/'}

    if not os.path.isdir(target_dir):
        return 400, {'error': f'Folder not found: src/{folder}'}

    target = os.path.join(target_dir, filename)
    try:
        with open(target, 'w') as f:
            f.write(content)
    except OSError as e:
        return 500, {'error': f'Write failed: {e}'}

    return 200, {'ok': True, 'saved': f'src/{folder}/{filename}'}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)

    def do_POST(self):
        if self.path in ('/save.php', '/save'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            status, result = handle_save(body)
            response = json.dumps(result).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        # Suppress asset noise, only show page loads and POSTs
        path = str(args[0]) if args else ''
        if any(s in path for s in ('skulpt', 'codemirror', '.js', '.css')):
            return
        super().log_message(fmt, *args)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f'alba-trinket local server — http://localhost:{port}/')
    print(f'Token: {"loaded from deploy.cfg" if SAVE_TOKEN else "not found"}')
    print(f'Open:  http://localhost:{port}/out/trinket1.html?mode=teacher')
    http.server.test(HandlerClass=Handler, port=port, bind='0.0.0.0')
