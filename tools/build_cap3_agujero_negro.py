#!/usr/bin/env python3
"""Construye el cap 3 «El agujero negro del control» del audiolibro-estudio
sobre «La trampa de la felicidad» (Russ Harris).

Cap sobre por qué fallan los intentos habituales de controlar los
pensamientos y sentimientos. Presenta la evitación experiencial y
las estrategias de forcejeo.
"""
import re

EYEBROW = "La trampa de la felicidad · notas de estudio"
TITLE = "El agujero negro del control"
SUBTITLE = "Russ Harris — manejo de la ansiedad con ACT"

CONTENT = [
    ("section", "Idea central"),
    ("lead",
     'Este capítulo explica por qué fallan nuestros intentos habituales de manejar la ansiedad. La clave: tenemos mucho menos control sobre nuestros pensamientos y sentimientos del que creemos, y esforzarnos por controlarlos suele empeorar las cosas. La solución es el problema.'),

    ("section", "Mito 3: es fácil controlar lo que piensas y sientes"),
    'Este mito lo sostienen casi todos los libros de autoayuda —«cambia los pensamientos negativos por positivos»—. Es falso: los pensamientos negativos siempre regresan, y las emociones incómodas —ira, miedo, tristeza, culpa, vergüenza— vuelven aunque las apartemos un rato. Regla clave: cuanto más intensa la emoción y más estresante la situación, menos control tenemos.',
    'Los experimentos que lo demuestran son varios: intentar no pensar en un helado, borrar un recuerdo, «desensibilizar» una pierna, no pensar en nada durante dos minutos mirando una estrella, el escenario del polígrafo. Ninguno funciona.',

    ("section", "La ilusión de control"),
    'Podemos moldear el mundo externo —refugio, comida, herramientas—, así que creemos que podemos controlar también el mundo interno. Las estrategias de control funcionan bien con lo material, pero no con pensamientos y emociones. El mito se refuerza porque los demás parecen felices, pero esconden sus luchas: Penny y las madres del grupo sufrían en secreto creyéndose las únicas.',

    ("section", "La solución es el problema"),
    'Cuando forcejeamos con los pensamientos y sentimientos difíciles para librarnos de ellos, a menudo empeoramos la vida. La analogía del eczema: rascarse alivia un instante pero libera histamina y aumenta el picor, un círculo vicioso. Ejemplos del libro: Joe evita socializar y se siente más rechazado; María bebe por ansiedad social y paga resaca y vergüenza; Prisha come chocolate y luego se siente peor; Alexei trabaja más para evitar la tensión y tensa más la relación.',

    ("section", "Las estrategias de forcejeo: dos grandes grupos"),
    'Estrategias de lucha —enfrentar o dominar los pensamientos y sentimientos—:',
    ("list", [
        'Reprimir: sacarlos por la fuerza o enterrarlos.',
        'Discutir: argumentar contra tus pensamientos.',
        'Asumir el control: «¡alégrate!», «¡tranquilízate!», forzar pensamientos positivos.',
        'Cuestionarse: criticarte con dureza para obligarte a sentir de otra manera.',
    ]),
    'Estrategias de huida —escapar o evitar—:',
    ("list", [
        'Decir que no: evitar situaciones, abandonar, procrastinar.',
        'Distraerse: centrarse en otra cosa —tabaco, comida, compras, videojuegos—.',
        'Consumo de sustancias: drogas, alcohol, azúcar, comida basura, tabaco.',
    ]),

    ("section", "El problema no es usarlas: es abusar de ellas"),
    'No hay problema en usar estrategias de forcejeo siempre que sea con moderación y sentido común, en situaciones donde es realista que funcionen, y que no te impidan comportarte como quieres ni hacer lo que te importa. La distracción tras un mal día puede ser la mejor opción.',
    'Se vuelven un problema cuando:',
    ("olist", [
        'Se usan en exceso: adicción, más complicaciones, más dolor. La historia del propio Harris con el chocolate Tim Tam, su sobrepeso e hipertensión.',
        'Se usan donde no pueden funcionar: el duelo. Donna y el alcohol tras perder a su familia. La analogía de la pelota bajo el agua: mientras aprietas se queda abajo, pero al soltarla salta con fuerza.',
        'Nos impiden hacer lo que importa: el miedo escénico que te aparta del escenario; evitar las emociones del divorcio con comida basura o alcohol.',
    ]),

    ("section", "Evitación experiencial"),
    'El término técnico es evitación experiencial: el intento continuado de evitar o librarse de experiencias internas no deseadas. Es normal y sin problema en niveles bajos. En niveles altos —uso excesivo de forcejeo— tiene tres costes:',
    ("olist", [
        'Consume tiempo y energía que podrían ir a avances.',
        'Los pensamientos y sentimientos regresan, a menudo con más intensidad.',
        'Reduce la calidad de vida a largo plazo, se vuelve un distanciamiento. Es un factor principal en ansiedad, depresión, adicciones, baja autoestima, trastornos alimentarios, trastorno obsesivo compulsivo, trauma, dolor crónico.',
    ]),
    'A veces el forcejeo es automático e inconsciente: por ejemplo, el nervio vago que anestesia ante dolor intenso, la sensación de vacío o de estar muerto por dentro.',

    ("section", "No solo el qué, también el porqué: la motivación"),
    'Lo que importa no es solo lo que haces, sino tu motivación. Cuidar amigos, trabajar, donar, hacer deporte pueden ser acciones guiadas por valores —mejoran la vida— o estrategias de forcejeo si su objetivo principal es huir de un sentimiento. Cuando la motivación es la evitación, se pierde la alegría y la vitalidad de lo que haces.',

    ("section", "El caso Michelle"),
    'Su vida se basa en evitar la sensación de no encajar y no valer nada. Los pensamientos recurrentes: «nadie va a quererme», «¿por qué no encajo?». Se esfuerza por complacer a todos, algo aprendido de niña con padres abusivos, donde complacer la protegía. De adulta, ponerse siempre la última refuerza su sensación de no valer nada. Cayó en la trampa de la felicidad.',

    ("section", "¿Cómo huir de la trampa?"),
    'El primer paso es ser consciente de ella: observar qué haces cada día para evitar el malestar y anotar las consecuencias. Llevar un diario ayuda. No significa resignarse a sufrir; eso sería modo obediente. En la segunda parte del libro se aprenden formas nuevas y eficaces —distintas del forcejeo y de la obediencia— de gestionar los pensamientos y sentimientos difíciles.',

    ("section", "Ejercicio del capítulo"),
    ("olist", [
        '¿Qué has intentado ya? Lista todas tus estrategias de forcejeo: distracciones, decir que no, estrategias mentales, sustancias, otras. Hazlo con curiosidad, sin juzgarte.',
        '¿Qué tal ha funcionado a largo plazo? ¿De verdad te libran del dolor de forma permanente? ¿Cuánto tarda en volver?',
        '¿Cuánto te ha costado? Marca la frecuencia, de nunca a siempre. Cuanto más a la derecha, mayor tu nivel de evitación experiencial. Tres descubrimientos esperables: has invertido mucho forcejeando; el alivio es temporal; y en exceso, estas estrategias tienen costes reales en dinero, tiempo, salud y relaciones.',
    ]),
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
    new_nav = ('<nav class="nav-foot">'
               '<a class="prev" href="el-punto-de-eleccion.html">El punto de elección</a>'
               '<a class="idx" href="index.html">Índice</a>'
               '<span></span></nav>')
    out = re.sub(r'<nav class="nav-foot">.*?</nav>',
                 lambda _m: new_nav, out, count=1, flags=re.DOTALL)
    out = out.replace('audio/tres-regimenes.mp3', 'audio/agujero-negro-del-control.mp3')
    out = out.replace('audio/tres-regimenes.alignment.json',
                      'audio/agujero-negro-del-control.alignment.json')
    out = out.replace('data-storage-key="tres-regimenes"',
                      'data-storage-key="agujero-negro-del-control"')

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

    open('agujero-negro-del-control.html', 'w', encoding='utf-8').write(out)
    n_par = sum(1 for it in CONTENT if isinstance(it, str) or (isinstance(it, tuple) and it[0] == "lead"))
    n_sec = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "section")
    n_ul = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "list")
    n_ol = sum(1 for it in CONTENT if isinstance(it, tuple) and it[0] == "olist")
    print(f"agujero-negro-del-control.html regenerado: {n_par} párrafos, {n_sec} secciones, {n_ul} listas ul, {n_ol} listas ol")


if __name__ == "__main__":
    main()
