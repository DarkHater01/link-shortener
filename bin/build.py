#!/usr/bin/env python3
"""Compila un sitio estatico de redirecciones a partir de los issues del repo.

Entrada : links.json  ->  [{"title": "slug", "body": "texto con la URL"}, ...]
Salida  : <outdir>/index.html  y  <outdir>/s/<slug>/index.html

La URL y el slug vienen de fuera (issues), o sea de un limite de confianza:
por eso se validan y se escapan. Nada de javascript:/data:, slugs solo [A-Za-z0-9_-].
"""
import html
import json
import re
import sys
from pathlib import Path

SLUG_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def slug_of(title):
    return re.sub(r"[^A-Za-z0-9]+", "-", (title or "").strip().lower()).strip("-")


def destination(body):
    """Primera linea del cuerpo que sea una URL http(s) valida."""
    for line in (body or "").splitlines():
        line = line.strip()
        if line.lower().startswith(("http://", "https://")):
            return line
    return None


def build(links, outdir):
    """Escribe el sitio. Devuelve (publicados, omitidos)."""
    out = Path(outdir)
    (out / "s").mkdir(parents=True, exist_ok=True)
    published, skipped = [], []
    for item in links:
        slug = slug_of(item.get("title", ""))
        url = destination(item.get("body", ""))
        if not SLUG_RE.match(slug) or not url:
            skipped.append(item.get("title", "?"))
            continue
        esc = html.escape(url, quote=True)
        page = (
            "<!doctype html><html lang=es><head><meta charset=utf-8>"
            f'<meta http-equiv=refresh content="0; url={esc}">'
            f'<link rel=canonical href="{esc}"><title>Redirigiendo...</title>'
            f'</head><body><p>Redirigiendo a <a href="{esc}">{esc}</a>...</p></body></html>'
        )
        d = out / "s" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        published.append((slug, url))
    rows = "\n".join(
        f'<li><a href="s/{html.escape(s, quote=True)}">{html.escape(s)}</a> &rarr; '
        f'<a href="{html.escape(u, quote=True)}">{html.escape(u)}</a></li>'
        for s, u in sorted(published)
    )
    (out / "index.html").write_text(
        "<!doctype html><html lang=es><head><meta charset=utf-8>"
        "<title>Enlaces</title></head><body><h1>Enlaces</h1>"
        f"<ul>{rows}</ul></body></html>",
        encoding="utf-8",
    )
    return published, skipped


def main():
    links = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    published, skipped = build(links, sys.argv[2])
    print(f"{len(published)} enlaces publicados, {len(skipped)} omitidos")
    for s in skipped:
        print(f"  omitido: {s!r}")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        assert slug_of("Mi Link Guay") == "mi-link-guay"
        assert slug_of("../../etc/passwd") == "etc-passwd"  # sin traversal
        assert not SLUG_RE.match("")
        assert not SLUG_RE.match("a" * 65)
        assert destination("mira esto\n  https://ejemplo.com/x  \nok") == "https://ejemplo.com/x"
        assert destination("javascript:alert(1)") is None
        assert destination("data:text/html,x") is None
        assert destination("sin url") is None
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            pub, skip = build(
                [
                    {"title": "ok", "body": "https://a.example/x"},
                    {"title": "malo", "body": "javascript:alert(1)"},
                    {"title": 'x"><script>', "body": "https://b.example/y</script><script>alert(1)"},
                ],
                t,
            )
            assert [p[0] for p in pub] == ["ok", "x-script"], pub  # titulo sucio -> slug sano
            assert len(skip) == 1, skip  # solo el javascript:
            assert 'url=https://a.example/x' in Path(t, "s", "ok", "index.html").read_text()
            evil = Path(t, "s", "x-script", "index.html").read_text()
            assert "<script>" not in evil and "&lt;script&gt;" in evil  # URL escapada
        print("selftest ok")
    else:
        main()
