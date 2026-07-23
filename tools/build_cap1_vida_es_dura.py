#!/usr/bin/env python3
"""Construye el cap 1 «La vida es dura» del audiolibro-estudio sobre
«La trampa de la felicidad» (Russ Harris).

Formato: notas de estudio con secciones y listas (h2 + p + ul + li).
Misma voz TTS que el proyecto anterior (Abel), mismo pipeline
(builder → HTML → generate_audio → inject_word_spans → MD).

Estructura del cap 1:
  - Idea central (párrafo)
  - Qué es la ACT (párrafo)
  - La «trampa de la felicidad» (párrafo)
  - ¿Es normal la felicidad? (párrafo)
  - ¿Por qué es difícil ser feliz? (párrafo + lista)
  - Los dos mitos que hacen daño (lista)
  - Dos significados de «felicidad» (lista)
  - La reacción escéptica de tu propia mente (párrafo)
  - Para llevar (párrafo)
"""
import re

EYEBROW = "La trampa de la felicidad · notas de estudio"
TITLE = "La vida es dura"
SUBTITLE = "Russ Harris — manejo de la ansiedad con ACT"

# Tipos de items:
#   ("lead", texto)                 → primer párrafo con capital
#   "texto"                         → párrafo normal
#   ("section", título)             → subtítulo de sección (h2)
#   ("list", [items])               → lista con viñetas
CONTENT = [
    ("section", "Idea central"),
    ("lead",
     'Ser humano duele. La vida trae momentos de alegría, pero también soledad, rechazo, fracaso y pérdida. El sufrimiento psicológico no es un defecto personal: es parte natural de estar vivo. El objetivo del libro no es eliminar el dolor, sino aprender a relacionarnos distinto con él y construir una vida con sentido.'),

    ("section", "Qué es la ACT"),
    'Terapia de Aceptación y Compromiso —ACT, se pronuncia «act», como «actúa»—. Desarrollada por Steven C. Hayes y colegas, Kelly Wilson y Kirk Strosahl, a mediados de los años ochenta. Basada en evidencia, con más de tres mil estudios. Eficaz para ansiedad, depresión, adicciones, dolor crónico, trauma, y también para rendimiento y bienestar.',

    ("section", "La trampa de la felicidad"),
    'Vivimos aferrados a creencias erróneas sobre la felicidad. Parecen lógicas, pero crean círculos viciosos: cuanto más perseguimos «sentirnos bien todo el tiempo», más sufrimos. La trampa está tan escondida que ni notamos que estamos en ella.',

    ("section", "¿Es normal la felicidad?"),
    'No. Las estadísticas de sufrimiento —depresión, ansiedad y demás— muestran que la felicidad duradera no es el estado normal del ser humano. Lo normal es un flujo cambiante de emociones, agradables y dolorosas.',

    ("section", "¿Por qué es difícil ser feliz?"),
    'La mente evolucionó para sobrevivir, no para ser feliz. Es, en el fondo, una mente de la Edad de Piedra funcionando en un mundo moderno. Está diseñada para:',
    ("list", [
        'Detectar peligros y anticipar amenazas —hoy: perder el empleo, hacer el ridículo, enfermar—.',
        'Pertenecer al grupo, y por eso compararnos constantemente con los demás.',
        'Buscar siempre «más y mejor», lo que produce una insatisfacción crónica.',
    ]),

    ("section", "Los dos mitos que hacen daño"),
    ("list", [
        'Mito uno: la felicidad es nuestro estado natural. Falso. Lo natural es sentir toda la gama de emociones.',
        'Mito dos: si no eres feliz, tienes un defecto. Falso. Si no eres feliz, eres normal. Crear una vida mejor exige estar dispuesto a sentir emociones incómodas.',
    ]),

    ("section", "Dos significados de «felicidad»"),
    ("list", [
        'Hedonía: sentirse bien, placer. Efímero. Perseguirlo como meta principal aumenta la ansiedad y la depresión.',
        'Eudemonía: vivir una vida plena y con sentido, guiada por los valores propios. Este es el foco del libro.',
    ]),

    ("section", "La reacción escéptica de tu propia mente"),
    'Es esperable pensar «esto no me va a funcionar». Conviene recordar dos cosas. Primero: es completamente normal, es lo que hace la mente. Segundo: la mente no intenta complicarte la vida; intenta mantenerte a salvo del dolor.',

    ("section", "Para llevar"),
    'El libro no promete eliminar la ansiedad, sino enseñar habilidades para restarle poder a los pensamientos y sentimientos dolorosos —«destrabarse» de ellos— y construir una vida rica y con sentido. Tómalo con calma, como un viaje.',
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
    parts.append('\n  </div>\n\n</article>')
    article = ''.join(parts)

    sk = open('tres-regimenes.html', encoding='utf-8').read()
    out = sk
    out = re.sub(r'<title>.*?</title>',
                 f'<title>{TITLE} — La trampa de la felicidad</title>',
                 out, count=1, flags=re.DOTALL)
    out = re.sub(r'<article class="page"[^>]*>.*?</article>',
                 lambda _m: article, out, count=1, flags=re.DOTALL)
    # Nav-foot: sin prev (es el primer cap), next apunta a cap 2.
    new_nav = ('<nav class="nav-foot">'
               '<span></span>'
               '<a class="idx" href="index.html">Índice</a>'
               '<a class="next" href="el-punto-de-eleccion.html">El punto de elección</a></nav>')
    out = re.sub(r'<nav class="nav-foot">.*?</nav>',
                 lambda _m: new_nav, out, count=1, flags=re.DOTALL)
    out = out.replace('audio/tres-regimenes.mp3', 'audio/la-vida-es-dura.mp3')
    out = out.replace('audio/tres-regimenes.alignment.json',
                      'audio/la-vida-es-dura.alignment.json')
    out = out.replace('data-storage-key="tres-regimenes"',
                      'data-storage-key="la-vida-es-dura"')

    # CSS extra para h2.section-subtitle y ul/li (no están en el esqueleto)
    extra_css = """
/* ===== Subtítulos de sección + listas para el formato de notas ===== */
.prose h2.section-subtitle {
  font-family: var(--font-body); font-weight: 400;
  font-size: 1.15rem; letter-spacing: 0.02em;
  color: var(--ink); margin: 2.6rem 0 0.9rem;
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}
.prose ul {
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
"""
    out = out.replace('</style>', extra_css + '</style>', 1)

    open('la-vida-es-dura.html', 'w', encoding='utf-8').write(out)
    n_par = sum(1 for it in CONTENT if isinstance(it, str) or (isinstance(it, tuple) and it[0] == "lead"))
    n_sec = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "section")
    n_list = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "list")
    print(f"la-vida-es-dura.html regenerado: {n_par} párrafos, {n_sec} secciones, {n_list} listas")


if __name__ == "__main__":
    main()
