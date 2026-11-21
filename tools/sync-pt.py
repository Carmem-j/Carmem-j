#!/usr/bin/env python3
"""Escreve o texto em portugues (translations.json -> pt) direto no HTML.

O HTML passa a ter o conteudo padrao em PT (sem "flash" vazio e com fallback se o
translations.json falhar). O JavaScript continua trocando os textos quando o idioma
ativo e EN. A fonte da verdade e sempre translations.json: edite la e rode este script.

Uso (na raiz do projeto):  python tools/sync-pt.py
E idempotente: rodar de novo sem mudar o JSON nao altera nenhum arquivo.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PT = json.load(open("translations.json", encoding="utf-8"))["pt"]
VOID = {"img", "br", "hr", "input", "meta", "link"}
TOC_ICONS = ["sh-circle", "sh-square", "sh-tri", "sh-flower"]
OPEN_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b([^<>]*?)>", re.S)


def find_close(s, tag, start):
    """Posicao do </tag> que fecha o elemento aberto antes de `start` (conta aninhamento)."""
    depth = 1
    pat = re.compile(rf"<(/?){tag}\b[^<>]*?>", re.I | re.S)
    for m in pat.finditer(s, start):
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.start()
        elif not m.group(0).endswith("/>"):
            depth += 1
    return -1


def set_attr(tag_src, attr, value):
    value = html.escape(value, quote=True)
    if re.search(rf'\b{attr}="[^"]*"', tag_src):
        return re.sub(rf'\b{attr}="[^"]*"', lambda m: f'{attr}="{value}"', tag_src, count=1)
    return tag_src[:-1] + f' {attr}="{value}">'


def sync_text(s):
    out, pos, changed = [], 0, 0
    while True:
        m = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\b([^<>]*?\bdata-i18n="([^"]+)"[^<>]*?)>', re.S).search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        tag, key = m.group(1), m.group(3)
        end_open = m.end()
        if tag.lower() in VOID or key not in PT:
            out.append(s[pos:end_open])
            pos = end_open
            continue
        close = find_close(s, tag, end_open)
        if close < 0:
            out.append(s[pos:end_open])
            pos = end_open
            continue
        out.append(s[pos:end_open] + PT[key])
        if s[end_open:close] != PT[key]:
            changed += 1
        pos = close
    return "".join(out), changed


def sync_attrs(s):
    def fix(m):
        tag = m.group(0)
        for attr_i18n, attr in (("data-i18n-alt", "alt"), ("data-i18n-label", "aria-label")):
            k = re.search(rf'{attr_i18n}="([^"]+)"', tag)
            if k and k.group(1) in PT:
                tag = set_attr(tag, attr, PT[k.group(1)])
        return tag

    return re.sub(r"<[a-zA-Z][^<>]*?data-i18n-(?:alt|label)=\"[^\"]+\"[^<>]*?>", fix, s, flags=re.S)


def sync_toc(s):
    """Indice lateral dos cases: ids nas secoes + links em PT (o JS reconstroi no idioma ativo)."""
    if 'class="case-content"' not in s or "<div data-toc>" not in s:
        return s
    body = re.search(r'<div class="case-content">', s)
    n = 0

    def add_id(m):
        nonlocal n
        n += 1
        return f'<section class="cs" id="cs-{n}">'

    head, tail = s[: body.start()], s[body.start():]
    tail = re.sub(r'<section class="cs"(?: id="[^"]*")?>', add_id, tail)
    links = []
    for i, sec in enumerate(re.finditer(r'<section class="cs" id="(cs-\d+)">.*?<h2[^>]*data-i18n="([^"]+)"', tail, re.S)):
        sid, key = sec.group(1), sec.group(2)
        icon = TOC_ICONS[i % len(TOC_ICONS)]
        links.append(
            f'<a href="#{sid}" data-go="{sid}"><svg aria-hidden="true"><use href="#{icon}"></use></svg><span>{PT[key]}</span></a>'
        )
    head = re.sub(r"(<div data-toc>).*?(</div>)", lambda m: m.group(1) + "".join(links) + m.group(2), head, flags=re.S)
    return head + tail


total = 0
for path in ["index.html"] + sorted(glob.glob("components/*.html")):
    src = open(path, encoding="utf-8").read()
    s, changed = sync_text(src)
    s = sync_attrs(s)
    s = sync_toc(s)
    if s != src:
        open(path, "w", encoding="utf-8", newline="\n").write(s)
        total += 1
        print(f"atualizado: {path}")
print(f"{total} arquivo(s) atualizado(s)")
sys.exit(0)
