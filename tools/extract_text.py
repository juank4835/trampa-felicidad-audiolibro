#!/usr/bin/env python3
"""
Extrae texto plano de un capítulo HTML del libro, listo para TTS.
Estrategia: aislar el <body>, eliminar bloques que no se leen (head, style,
script, nav, .chapter-eyebrow), y luego despojar los tags restantes
manteniendo solo el texto.
"""
import sys
import re


def extract(html: str) -> str:
    # 1. quedarnos solo con el contenido del <body>
    m = re.search(r"<body[^>]*>(.*?)</body>", html, flags=re.DOTALL | re.IGNORECASE)
    body = m.group(1) if m else html

    # 2. eliminar bloques que no se leen
    for pat in [
        r"<style[^>]*>.*?</style>",
        r"<script[^>]*>.*?</script>",
        r"<nav[^>]*>.*?</nav>",
        # divs/elementos con class chapter-eyebrow
        r'<div[^>]*class="[^"]*chapter-eyebrow[^"]*"[^>]*>.*?</div>',
        # reproductor flotante (pill v2 trae botones "15", "1×", "0:00" que se cuelan como texto)
        r'<aside[^>]*class="[^"]*audio-pill[^"]*"[^>]*>.*?</aside>',
        # toolbar de subrayado (lo crea JS pero por si acaso aparece en el HTML estático)
        r'<div[^>]*class="[^"]*hl-toolbar[^"]*"[^>]*>.*?</div>',
        # cajas marcadas no-audio (recuadros de datos, citas): se ven pero NO se narran
        r'<aside[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</aside>',
        r'<blockquote[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</blockquote>',
        r'<cite[^>]*class="[^"]*no-audio[^"]*"[^>]*>.*?</cite>',
        # ornament visual «• • •»: decorativo, NO debe leerse (el TTS
        # lo pronunciaría como tres puntos sueltos y desalinearía los
        # spans karaoke).
        r'<div[^>]*class="[^"]*ornament[^"]*"[^>]*>.*?</div>',
        # UI de usabilidad-v1 (skip-link, panel de ajustes, barra de progreso,
        # botón «continuar donde ibas», tarjeta «siguiente capítulo»): nada de
        # esto debe llegar al TTS — no es contenido del libro
        r'<a[^>]*class="[^"]*skip-link[^"]*"[^>]*>.*?</a>',
        r'<div[^>]*class="[^"]*ui-settings[^"]*"[^>]*>.*?</div>\s*</div>',
        r'<div[^>]*class="[^"]*read-progress[^"]*"[^>]*>.*?</div>',
        r'<button[^>]*class="[^"]*resume-read[^"]*"[^>]*>.*?</button>',
        r'<div[^>]*class="[^"]*next-card[^"]*"[^>]*>.*?</div>',
    ]:
        body = re.sub(pat, "", body, flags=re.DOTALL | re.IGNORECASE)

    # 3. introducir doble salto antes de cada elemento de bloque para
    #    preservar separación entre párrafos al despojar tags
    for tag in ("p", "h1", "h2", "h3", "blockquote", "figcaption", "li", "div", "aside", "cite"):
        body = re.sub(
            rf"<{tag}\b[^>]*>", lambda _m, t=tag: f"\n\n[[{t}]]", body, flags=re.IGNORECASE
        )

    # 4. quitar todos los tags restantes
    text = re.sub(r"<[^>]+>", "", body)

    # 5. quitar los marcadores [[tag]] (solo nos sirvieron como ancla de salto)
    text = re.sub(r"\[\[[a-z0-9]+\]\]", "", text)

    # 6. decodificar entidades HTML comunes
    entities = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&apos;": "'", "&mdash;": "—", "&ndash;": "–",
        "&hellip;": "…", "&laquo;": "«", "&raquo;": "»",
        "&iexcl;": "¡", "&iquest;": "¿",
    }
    for k, v in entities.items():
        text = text.replace(k, v)
    # decodificar entidades numéricas
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)

    # 7. normalizar espacios
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def main():
    if len(sys.argv) < 2:
        print("uso: extract_text.py archivo.html", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        html = f.read()
    print(extract(html))


if __name__ == "__main__":
    main()
