#!/usr/bin/env python3
"""Construye el cap 2 «El punto de elección» del audiolibro-estudio sobre
«La trampa de la felicidad» (Russ Harris).

Novedades respecto al cap 1:
  - Nuevo tipo de item ("olist", [...])  →  lista NUMERADA <ol>
    (usada en «Tres claves para que el libro funcione»).
  - Sigue usando ("list", [...])  →  lista con viñeta <ul>.
"""
import re

EYEBROW = "La trampa de la felicidad · notas de estudio"
TITLE = "El punto de elección"
SUBTITLE = "Russ Harris — manejo de la ansiedad con ACT"

CONTENT = [
    ("section", "Idea central"),
    ("lead",
     'Siempre estamos haciendo algo, y cada comportamiento nos acerca o nos aleja de la vida que queremos. Este capítulo presenta el punto de elección, la herramienta visual que se usa durante todo el libro.'),

    ("section", "Avances y distanciamientos"),
    ("list", [
        'Avances: cosas que dices y haces que te acercan a la vida que quieres construir y a la persona que quieres ser —cuidar relaciones, salud, hobbies, ser amable, crecer—. No hay una lista «oficial»: cada quien decide.',
        'Distanciamientos: cosas que te alejan o empeoran tu vida a largo plazo —pelear o aislarte, evitar el ejercicio, sustancias, procrastinar—. Incluyen procesos mentales: preocuparse, rumiar, obsesionarse, sobreanalizar.',
    ]),

    ("section", "Principio clave para tatuarse en la frente"),
    'Todas las actividades pueden ser avances o distanciamientos según el momento. El término técnico es «productividad», en inglés workability: si algo te acerca a la vida que quieres, es un avance; si te aleja, un distanciamiento. Tú eres la única persona que puede decidirlo.',

    ("section", "Qué desencadena los distanciamientos"),
    'Las situaciones, pensamientos y sentimientos difíciles. El libro usa este término para todas las experiencias internas desagradables: ansiedad, tristeza, ira, culpa, impulsos, recuerdos, sensaciones físicas.',

    ("section", "Trabarse: dos modos que suelen solaparse"),
    ("list", [
        'Modo obediente: los pensamientos y sentimientos nos dominan y dictan nuestras acciones. Les obedecemos —nos rendimos, gritamos, cedemos a un hábito—.',
        'Modo forcejeo: intentamos activamente evitar, suprimir o huir de ellos —drogas, alcohol, comida basura, procrastinación, aislamiento— para un alivio momentáneo, aunque nos perjudique.',
    ]),

    ("section", "La ecuación central"),
    'Trabarse más distanciarse igual a sufrimiento psicológico. Casi todos los trastornos —ansiedad, depresión, adicciones, trastorno obsesivo compulsivo y demás— nacen de este proceso básico.',

    ("section", "Destrabarse y avanzar"),
    ("list", [
        'Valores: tus deseos más profundos sobre cómo quieres comportarte y tratar a los demás. Funcionan como brújula interna y como fuente de motivación. El ejercicio de los roles ayuda a identificar cómo quieres comportarte en una relación importante.',
        'Habilidades para destrabarse: permiten soltar los pensamientos y sentimientos difíciles antes de que te arrastren a un distanciamiento. Cuanto mejor se te dé, más posibilidad real de elegir.',
    ]),

    ("section", "El punto de elección"),
    'Diagrama creado por Harris con Joe Ciarrochi y Ann Bailey para simplificar el modelo ACT. En los momentos difíciles siempre podemos elegir avanzar o distanciarnos, pero solo podremos elegir si hemos desarrollado habilidades para destrabarnos.',

    ("section", "Tres claves para que el libro funcione"),
    ("olist", [
        'Considéralo todo un experimento. Prueba con actitud abierta y curiosa; quédate con lo que te sirva, adapta o abandona lo que no.',
        'Ten por seguro que tu mente interferirá. El «dispensador de excusas»: «esto no me va a funcionar», «no tengo tiempo», «no estoy de humor». Reconócelo como tu mente intentando protegerte.',
        'La práctica es imprescindible. No se aprende una habilidad solo leyendo; hay que hacer los ejercicios una y otra vez.',
    ]),

    ("section", "Ejercicio: rellenar tu punto de elección"),
    ("list", [
        'Parte A, tus trabas: las cuatro o cinco situaciones más difíciles de tu vida actual; las emociones y sensaciones más difíciles; impulsos o necesidades; y pensamientos recurrentes que no ayudan —autocríticas, creencias rígidas, pronósticos negativos—.',
        'Parte B, tus distanciamientos: acciones y procesos mentales improductivos que haces en modo obediente o forcejeo. Son cosas que haces, no que sientes.',
        'Parte C, tus avances: lo que ya haces que te acerca a tu vida —por ejemplo, leer este libro— y lo que te gustaría empezar a hacer, guiado por tus valores. También son cosas que haces, no estados como «estar tranquilo».',
    ]),

    ("section", "¿Y ahora qué?"),
    'Escucha lo que tu mente dice ante todo esto: entusiasmo, escepticismo, ansiedad, dudas. Si te empuja a abandonar, estás ante un punto de elección: reconocer que intenta protegerte de la incomodidad y seguir adelante.',
]


def main():
    parts = ['<article class="page" id="contenido" tabindex="-1">\n',
             f'\n  <div class="chapter-eyebrow">{EYEBROW}</div>\n',
             f'  <h1 class="chapter-title">{TITLE}</h1>\n',
             f'  <p class="chapter-subtitle">{SUBTITLE}</p>\n',
             '\n  <div class="ornament">• • •</div>\n',
             '\n  <div class="prose">\n']
    for it in CONTENT:
        if isinstance(it, str):
            parts.append(f'    <p>{it}</p>\n')
        elif it[0] == "lead":
            parts.append(f'    <p class="lead">{it[1]}</p>\n')
        elif it[0] == "section":
            parts.append(f'\n    <h2 class="section-subtitle">{it[1]}</h2>\n')
        elif it[0] == "list":
            parts.append('    <ul>\n')
            for li in it[1]:
                parts.append(f'      <li>{li}</li>\n')
            parts.append('    </ul>\n')
        elif it[0] == "olist":
            parts.append('    <ol class="numerada">\n')
            for li in it[1]:
                parts.append(f'      <li>{li}</li>\n')
            parts.append('    </ol>\n')
    parts.append('\n  </div>\n\n</article>')
    article = ''.join(parts)

    sk = open('tres-regimenes.html', encoding='utf-8').read()
    out = sk
    out = re.sub(r'<title>.*?</title>',
                 f'<title>{TITLE} — La trampa de la felicidad</title>',
                 out, count=1, flags=re.DOTALL)
    out = re.sub(r'<article class="page"[^>]*>.*?</article>',
                 lambda _m: article, out, count=1, flags=re.DOTALL)
    # Nav-foot: prev = cap 1, next = cap 3
    new_nav = ('<nav class="nav-foot">'
               '<a class="prev" href="la-vida-es-dura.html">La vida es dura</a>'
               '<a class="idx" href="index.html">Índice</a>'
               '<a class="next" href="agujero-negro-del-control.html">El agujero negro del control</a></nav>')
    out = re.sub(r'<nav class="nav-foot">.*?</nav>',
                 lambda _m: new_nav, out, count=1, flags=re.DOTALL)
    out = out.replace('audio/tres-regimenes.mp3', 'audio/el-punto-de-eleccion.mp3')
    out = out.replace('audio/tres-regimenes.alignment.json',
                      'audio/el-punto-de-eleccion.alignment.json')
    out = out.replace('data-storage-key="tres-regimenes"',
                      'data-storage-key="el-punto-de-eleccion"')

    # CSS extra: subtítulos + listas <ul> y <ol>
    extra_css = """
/* ===== Subtítulos de sección + listas para el formato de notas ===== */
.prose h2.section-subtitle {
  font-family: var(--font-body); font-weight: 400;
  font-size: 1.15rem; letter-spacing: 0.02em;
  color: var(--ink); margin: 2.6rem 0 0.9rem;
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}
.prose ul, .prose ol.numerada {
  list-style: none; padding-left: 0;
  margin: 1.1rem 0 1.8rem;
}
.prose ul li {
  position: relative; padding-left: 1.5rem;
  margin-bottom: 0.9rem; line-height: 1.7;
}
.prose ul li::before {
  content: '·';
  position: absolute; left: 0.4rem; top: -0.05em;
  color: var(--verde); font-weight: 700; font-size: 1.3em;
}
.prose ol.numerada {
  counter-reset: paso;
}
.prose ol.numerada li {
  counter-increment: paso;
  position: relative; padding-left: 2rem;
  margin-bottom: 1.1rem; line-height: 1.7;
}
.prose ol.numerada li::before {
  content: counter(paso) '.';
  position: absolute; left: 0.2rem; top: 0;
  color: var(--verde); font-weight: 400;
  font-variant-numeric: tabular-nums;
}
"""
    out = out.replace('</style>', extra_css + '</style>', 1)

    open('el-punto-de-eleccion.html', 'w', encoding='utf-8').write(out)
    n_par = sum(1 for it in CONTENT if isinstance(it, str) or (isinstance(it, tuple) and it[0] == "lead"))
    n_sec = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "section")
    n_ul = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "list")
    n_ol = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "olist")
    print(f"el-punto-de-eleccion.html regenerado: {n_par} párrafos, {n_sec} secciones, {n_ul} listas ul, {n_ol} listas ol")


if __name__ == "__main__":
    main()
