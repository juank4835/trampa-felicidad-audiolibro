#!/usr/bin/env python3
"""Genera UN SOLO archivo Markdown con TODO el libro concatenado.

Por qué Markdown y no PDF:
  - Los chats de Claude/GPT cuentan cada página de PDF como una imagen.
    Un libro de 90 páginas = 90 imágenes, llega al límite del chat en
    una sola subida.
  - Markdown es un solo archivo de texto. Cuenta como UN documento.
  - Las IAs lo procesan directamente como texto, sin OCR ni render.
  - Mucho más liviano: ~250 KB en lugar de 13 MB.
  - Preserva estructura semántica (títulos, citas, énfasis) que la IA
    puede usar para razonar mejor sobre el libro.

Estrategia:
  1. Toma el orden canónico de capítulos (igual que build_pdf.py).
  2. De cada HTML extrae:
     - eyebrow (Bloque I/II/…)
     - h1 (título del cap)
     - subtítulo
     - prose (todo el contenido del capítulo)
  3. Convierte cada elemento del prose a Markdown:
     - <p> → párrafo plano
     - <em> → *itálica*
     - <strong> → **negrita**
     - <blockquote class="pull-quote"> → > cita + atribución
     - <blockquote class="lema"> → > _MÁXIMA_ (énfasis)
     - <blockquote class="epigrafe"> → > epígrafe + atribución
     - <aside class="recuadro"> → recuadro con header en bold
  4. Sin spans karaoke, sin scripts, sin CSS, sin pill de audio.

Uso:
  build_book_md.py            → genera ./arregla-el-dinero.md
  build_book_md.py salida.md
"""
import re
import sys
from pathlib import Path
import html as html_lib

# Orden canónico del libro (mismo que build_pdf.py)
CHAPTERS = [
    # Bloque I · Fundamentos
    "dinero-como-informacion.html",
    "criterio-de-evaluacion.html",
    "tres-formas-organizar-dinero.html",
    # Bisagra entre Bloque I y Bloque II
    "cuando-un-precio-dice-la-verdad.html",
    # Bloque II · Los cimientos
    "preferencia-temporal.html",
    "ahorro-real.html",
    # Bloque III · La anatomía
    "tasa-de-interes.html",
    "asignacion-intertemporal.html",
    "deteccion-mala-inversion.html",
    "precios-relativos.html",
    "predictibilidad-estructural.html",
    "poder-adquisitivo.html",
    "asignacion-credito.html",
    "auditabilidad.html",
    # Bisagra
    "por-que-no-volver-al-oro.html",
    # Bloque IV
    "el-horizonte-se-acorta.html",
    "comerse-la-semilla.html",
    "el-estado-sin-freno.html",
    # Umbral de cierre
    "arregla-el-dinero-arregla-el-mundo.html",
]


def strip_spans(s: str) -> str:
    """Quita los <span class='w' data-w='N'>palabra</span> dejando la palabra."""
    return re.sub(r'<span class="w" data-w="\d+">([^<]+)</span>', r'\1', s)


def html_to_md_inline(s: str) -> str:
    """Convierte inline HTML a Markdown:
       <em> → *...*, <strong> → **...**, <br> → newline.
       Quita los spans karaoke y cualquier otro tag inline."""
    s = strip_spans(s)
    # br → newline
    s = re.sub(r'<br\s*/?>', '\n', s)
    # em
    s = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', s, flags=re.DOTALL)
    # strong
    s = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', s, flags=re.DOTALL)
    # quitar cualquier otro tag
    s = re.sub(r'<[^>]+>', '', s)
    # decode entidades html
    s = html_lib.unescape(s)
    # normalizar espacios (pero preservar saltos de línea)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    return s.strip()


def section_subtitle_md(html: str) -> str:
    """Convierte <span class='section-num'>...</span> + texto en heading MD."""
    # En el libro, los subtítulos de sección dentro del prose vienen como
    # <h2 class="section-subtitle"><span class="section-num">N</span> Título</h2>
    # o variantes. Los convertimos a `## N. Título`.
    return html_to_md_inline(html)


def extract_chapter(html: str) -> str:
    """Extrae el contenido del cap y lo devuelve como Markdown."""
    md = []

    # 1. Eyebrow (Bloque I · Fundamentos)
    m = re.search(r'<div class="chapter-eyebrow">(.*?)</div>', html, re.DOTALL)
    eyebrow = html_to_md_inline(m.group(1)) if m else ""

    # 2. Título
    m = re.search(r'<h1 class="chapter-title">(.*?)</h1>', html, re.DOTALL)
    if not m:
        raise RuntimeError("no encontré h1.chapter-title")
    title = html_to_md_inline(m.group(1))

    # 3. Subtítulo
    m = re.search(r'<p class="chapter-subtitle">(.*?)</p>', html, re.DOTALL)
    subtitle = html_to_md_inline(m.group(1)) if m else ""

    # Header del capítulo
    if eyebrow:
        md.append(f"_{eyebrow}_")
        md.append("")
    md.append(f"# {title}")
    if subtitle:
        md.append("")
        md.append(f"*{subtitle}*")
    md.append("")
    md.append("---")
    md.append("")

    # 4. Prose
    m = re.search(r'<div class="prose">(.*?)</div>\s*</article>', html, re.DOTALL)
    if not m:
        raise RuntimeError("no encontré div.prose")
    prose = m.group(1)

    # Iterar elementos top-level del prose, en orden de aparición.
    # Tipos: <p>, <blockquote>, <aside>, <h2>, <ol>, <ul>, <div class="ornament">
    # Hacemos un regex que matchee cualquier bloque top-level.
    element_re = re.compile(
        r'<(?P<tag>p|blockquote|aside|h2|h3|ol|ul|div)\b[^>]*>.*?</(?P=tag)>',
        re.DOTALL
    )

    for elem_m in element_re.finditer(prose):
        elem = elem_m.group(0)
        tag = elem_m.group('tag')

        # ornament (• • •) → separator
        if 'class="ornament"' in elem:
            md.append("· · ·")
            md.append("")
            continue

        # section subtitle (h2/h3)
        if tag in ('h2', 'h3'):
            text = html_to_md_inline(elem)
            md.append(f"## {text}")
            md.append("")
            continue

        # blockquote
        if tag == 'blockquote':
            cls = re.search(r'class="([^"]*)"', elem)
            cls = cls.group(1) if cls else ""

            # Saltar lo no-audio si tiene cite, pero el contenido va igual
            # porque en MD queremos preservar el contenido completo aunque
            # no se narre (las IAs leen todo).

            # cuerpo: todos los <p> dentro
            paras = re.findall(r'<p[^>]*>(.*?)</p>', elem, re.DOTALL)
            cite_m = re.search(r'<cite[^>]*>(.*?)</cite>', elem, re.DOTALL)

            if 'lema' in cls:
                # máxima: > _texto_ con énfasis fuerte
                for p in paras:
                    md.append(f"> **{html_to_md_inline(p)}**")
                md.append("")
            elif 'epigrafe' in cls:
                # epígrafe: cita + atribución
                for p in paras:
                    md.append(f"> *{html_to_md_inline(p)}*")
                if cite_m:
                    cite = html_to_md_inline(cite_m.group(1))
                    md.append(f">")
                    md.append(f"> — {cite}")
                md.append("")
            else:
                # pull-quote u otros: cita + atribución
                for p in paras:
                    md.append(f"> {html_to_md_inline(p)}")
                if cite_m:
                    cite = html_to_md_inline(cite_m.group(1))
                    md.append(f">")
                    md.append(f"> — {cite}")
                md.append("")
            continue

        # aside
        if tag == 'aside':
            # Saltar el pill de audio (audio-pill)
            if 'audio-pill' in elem:
                continue

            # recuadro: tag + contenido
            tag_m = re.search(r'<span class="recuadro-tag">(.*?)</span>', elem, re.DOTALL)
            recuadro_tag = html_to_md_inline(tag_m.group(1)) if tag_m else "Recuadro"
            paras = re.findall(r'<p[^>]*>(.*?)</p>', elem, re.DOTALL)
            md.append(f"> **{recuadro_tag.upper()}**")
            md.append(">")
            for i, p in enumerate(paras):
                text = html_to_md_inline(p)
                # cada línea del párrafo precedida por >
                for line in text.split('\n'):
                    md.append(f"> {line}")
                if i < len(paras) - 1:
                    md.append(">")
            md.append("")
            continue

        # listas
        if tag in ('ol', 'ul'):
            items = re.findall(r'<li[^>]*>(.*?)</li>', elem, re.DOTALL)
            marker = "1." if tag == 'ol' else "-"
            for it in items:
                md.append(f"{marker} {html_to_md_inline(it)}")
            md.append("")
            continue

        # párrafo (p)
        if tag == 'p':
            cls = re.search(r'class="([^"]*)"', elem)
            cls = cls.group(1) if cls else ""
            # saltar chapter-meta (lectura ≈ N min)
            if 'chapter-meta' in cls:
                continue
            text = html_to_md_inline(elem)
            if text:
                md.append(text)
                md.append("")
            continue

        # div misc (saltar)
        if tag == 'div':
            continue

    return "\n".join(md).rstrip() + "\n"


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("arregla-el-dinero.md")
    root = Path(__file__).resolve().parent.parent

    md_parts = []

    # Portada
    md_parts.append("# Arregla el dinero, arregla el mundo")
    md_parts.append("")
    md_parts.append("*Por qué el dinero que usamos define el mundo en que vivimos*")
    md_parts.append("")
    md_parts.append("**Juan Camilo Álvarez Ramírez**")
    md_parts.append("")
    md_parts.append("---")
    md_parts.append("")

    # Tabla de contenidos
    md_parts.append("## Tabla de contenidos")
    md_parts.append("")
    for i, fn in enumerate(CHAPTERS, 1):
        html = (root / fn).read_text(encoding="utf-8")
        m = re.search(r'<h1 class="chapter-title">(.*?)</h1>', html, re.DOTALL)
        title = html_to_md_inline(m.group(1)) if m else fn
        md_parts.append(f"{i}. {title}")
    md_parts.append("")
    md_parts.append("---")
    md_parts.append("")

    # Capítulos
    for i, fn in enumerate(CHAPTERS, 1):
        path = root / fn
        if not path.exists():
            print(f"⚠ falta {fn}, salto", file=sys.stderr)
            continue
        html = path.read_text(encoding="utf-8")
        try:
            md_parts.append(extract_chapter(html))
        except Exception as e:
            print(f"✗ error en {fn}: {e}", file=sys.stderr)
            continue
        # separador entre capítulos
        md_parts.append("")
        md_parts.append("---")
        md_parts.append("")

    out = "\n".join(md_parts)
    out_path.write_text(out, encoding="utf-8")

    # Stats
    kb = out_path.stat().st_size / 1024
    words = len(re.findall(r'\w+', out))
    print(f"OK: {out_path} ({kb:.0f} KB, {len(CHAPTERS)} capítulos, ~{words:,} palabras)")

    # Sincronizar la página de descarga con estos números.
    # La línea a actualizar en descargar-md.html es:
    #   "N capítulos · ~X palabras · ~Y KB"
    # Se localiza dentro del <p class="meta"> y se reescribe en formato
    # con separador de miles en español (punto).
    dl_path = root / "descargar-md.html"
    if dl_path.exists():
        # Formatea el número de palabras redondeado a la centena más cercana,
        # con separador de miles con punto (formato español).
        rounded = int(round(words, -2))
        formatted_words = f"{rounded:,}".replace(",", ".")
        new_stats = f"{len(CHAPTERS)} capítulos · ~{formatted_words} palabras · ~{kb:.0f} KB"
        html = dl_path.read_text(encoding="utf-8")
        # Reemplaza solo la línea de stats (el último <br> del <p class="meta">).
        new_html = re.sub(
            r'(<br>\s*\n\s*)\d+\s+cap[íi]tulos\s*·\s*~[\d\.,]+\s+palabras\s*·\s*~\d+\s*KB',
            r'\g<1>' + new_stats,
            html, count=1
        )
        if new_html != html:
            dl_path.write_text(new_html, encoding="utf-8")
            print(f"OK: {dl_path.name} sincronizado ({new_stats})")
        else:
            print(f"OK: {dl_path.name} ya tenía los mismos números")


if __name__ == "__main__":
    main()
