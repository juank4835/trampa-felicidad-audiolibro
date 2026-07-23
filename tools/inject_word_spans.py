#!/usr/bin/env python3
"""
Envuelve cada palabra del texto de un capítulo HTML con
<span class="w" data-w="N">palabra</span>, dentro de las secciones que
queremos sincronizar con el audio karaoke.

Definición de "palabra": secuencia alfanumérica unicode (\\w+).
La puntuación adyacente queda fuera del span (no se resalta), evitando
así HTML inválido por nesting cruzado con tags inline (em, strong, etc.).
"""
import re
import sys
from pathlib import Path


def wrap_words_in_block(html_block: str, start_idx: int) -> tuple[str, int]:
    """Envuelve cada secuencia \\w+ del texto de la sección."""
    # Pasada 1: construir texto plano + mapeo carácter→posición en html
    plain = []
    char_to_html = []
    pos = 0
    while pos < len(html_block):
        ch = html_block[pos]
        if ch == "<":
            end = html_block.find(">", pos)
            if end == -1:
                break
            pos = end + 1
        else:
            plain.append(ch)
            char_to_html.append(pos)
            pos += 1
    plain_text = "".join(plain)

    # Pasada 2: encontrar matches. Una "palabra" es \w+ permitiendo punto
    # entre dígitos (para «36.5») u otros separadores típicos (apóstrofo).
    ranges = []
    idx = start_idx
    word_re = re.compile(r"\w+(?:[.’']\w+)*", re.UNICODE)
    for m in word_re.finditer(plain_text):
        s, e = m.start(), m.end()
        # mapear a posiciones HTML
        html_start = char_to_html[s]
        html_end = char_to_html[e - 1] + 1
        ranges.append((html_start, html_end, idx))
        idx += 1

    # Pasada 3: insertar de atrás para adelante
    out = html_block
    for html_start, html_end, w_idx in reversed(ranges):
        content = out[html_start:html_end]
        # Solo envolver si NO contiene un tag completo (evita cruces).
        # Si la palabra cruza un tag, dividir es complejo; ignorar este caso
        # raro mantiene el HTML válido. Verificación rápida:
        if "<" in content or ">" in content:
            # palabra cruza un tag — saltarla, no envolver
            continue
        replacement = f'<span class="w" data-w="{w_idx}">{content}</span>'
        out = out[:html_start] + replacement + out[html_end:]

    return out, idx


def process_html(html: str) -> tuple[str, int]:
    counter = 0

    def repl_h1(m):
        nonlocal counter
        inner, counter = wrap_words_in_block(m.group(1), counter)
        return f'<h1 class="chapter-title">{inner}</h1>'

    html = re.sub(r'<h1 class="chapter-title">(.*?)</h1>', repl_h1, html, flags=re.DOTALL)

    def repl_sub(m):
        nonlocal counter
        inner, counter = wrap_words_in_block(m.group(1), counter)
        return f'<p class="chapter-subtitle">{inner}</p>'

    html = re.sub(r'<p class="chapter-subtitle">(.*?)</p>', repl_sub, html, flags=re.DOTALL)

    def repl_prose(m):
        nonlocal counter
        block = m.group(1)
        # Sacar las cajas no-audio (recuadros, citas) a placeholders para que
        # NO se envuelvan en spans ni consuman índices de palabra. Se restauran
        # tal cual después de envolver el resto. El placeholder es un comentario
        # HTML <!--NOAUDIOk-->: wrap_words lo trata como un tag y lo salta.
        stash = []

        def _stash(mm):
            stash.append(mm.group(0))
            return f'<!--NOAUDIO{len(stash) - 1}-->'

        block = re.sub(r'<aside\b[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</aside>',
                       _stash, block, flags=re.DOTALL)
        block = re.sub(r'<blockquote\b[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</blockquote>',
                       _stash, block, flags=re.DOTALL)
        block = re.sub(r'<cite\b[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</cite>',
                       _stash, block, flags=re.DOTALL)

        inner, counter = wrap_words_in_block(block, counter)

        for i, original in enumerate(stash):
            inner = inner.replace(f'<!--NOAUDIO{i}-->', original)
        return f'<div class="prose">{inner}</div>\n\n</article>'

    html = re.sub(
        r'<div class="prose">(.*?)</div>\s*</article>',
        repl_prose,
        html,
        flags=re.DOTALL,
        count=1,
    )

    return html, counter


def main():
    if len(sys.argv) < 2:
        print("uso: inject_word_spans.py <html> [salida]", file=sys.stderr)
        sys.exit(1)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else in_path
    html = in_path.read_text(encoding="utf-8")
    new_html, count = process_html(html)
    out_path.write_text(new_html, encoding="utf-8")
    print(f"OK: envueltas {count} palabras → {out_path}")


if __name__ == "__main__":
    main()
