#!/usr/bin/env python3
"""Genera audio + alignment para un capítulo desde cero.

Usa el endpoint /with-timestamps (igual que splice_audio.py), así
queda exactamente alineado con el resto del pipeline: spans karaoke
1:1 con el alignment, ffmpeg-concat consistente, mismo formato de
salida que el resto de los caps.

Uso (dos formas):
  generate_audio.py <texto.txt>  <out.mp3> [<out.alignment.json>]
  generate_audio.py <capítulo.html> <out.mp3>  <out.alignment.json>

Si la entrada es HTML, se extrae el texto narrable con extract_text.py
(mismo extractor que el resto del pipeline). Si es .txt, se usa tal cual.

Variables de entorno:
  ELEVENLABS_API_KEY   (requerida)
  ELEVENLABS_VOICE_ID  (requerida)
  ELEVENLABS_MODEL     (opcional, default eleven_multilingual_v2)
"""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

MAX_CHARS = 4500  # ElevenLabs eleven_multilingual_v2 acepta hasta ~5000
CTX_CHARS = 1000


def split_text(text, limit=MAX_CHARS):
    """Parte por párrafos sin partir oraciones. Cada chunk ≤ limit."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        cand = (cur + "\n\n" + p) if cur else p
        if len(cand) <= limit:
            cur = cand
        else:
            if cur:
                chunks.append(cur)
            if len(p) <= limit:
                cur = p
            else:
                # Párrafo solo excede el límite: partir por oraciones
                buf = ""
                for tok in p.replace("? ", "?|S|").replace("! ", "!|S|").replace(". ", ".|S|").split("|S|"):
                    c2 = (buf + " " + tok) if buf else tok
                    if len(c2) <= limit:
                        buf = c2
                    else:
                        if buf:
                            chunks.append(buf)
                        buf = tok
                cur = buf
    if cur:
        chunks.append(cur)
    return chunks


def tts(text, voice_id, api_key, model, prev_text="", next_text=""):
    body = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.65,
            "similarity_boost": 0.75,
            "style": 0.20,
            "use_speaker_boost": True,
        },
    }
    if prev_text:
        body["previous_text"] = prev_text[-CTX_CHARS:]
    if next_text:
        body["next_text"] = next_text[:CTX_CHARS]
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs error {e.code}: {e.read().decode()}")


def chars_to_words(characters, starts, ends):
    words, buf_c, buf_s, buf_e = [], [], [], []

    def flush():
        if not buf_c:
            return
        wt = "".join(buf_c)
        if wt.strip():
            words.append({"text": wt, "start": buf_s[0], "end": buf_e[-1]})
        buf_c.clear(); buf_s.clear(); buf_e.clear()

    for ch, s, e in zip(characters, starts, ends):
        if ch.isspace() or ch == "\n":
            flush()
        else:
            buf_c.append(ch); buf_s.append(s); buf_e.append(e)
    flush()
    return words


def ffprobe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]).decode().strip()
    return float(out)


def ffmpeg_normalize(src, dst):
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src),
         "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "1", str(dst)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def ffmpeg_concat(parts, dst):
    listfile = dst.parent / "concat.txt"
    abs_parts = [Path(p).resolve() for p in parts]
    listfile.write_text("\n".join(f"file '{p}'" for p in abs_parts) + "\n")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "1", str(dst)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    finally:
        if listfile.exists():
            listfile.unlink()


def main():
    if len(sys.argv) < 3:
        raise SystemExit(
            "uso:\n"
            "  generate_audio.py <texto.txt> <out.mp3> [<out.alignment.json>]\n"
            "  generate_audio.py <capítulo.html> <out.mp3> <out.alignment.json>"
        )
    in_path = Path(sys.argv[1])
    out_mp3 = Path(sys.argv[2])
    out_align = Path(sys.argv[3]) if len(sys.argv) >= 4 else None

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
    if not api_key or not voice_id:
        raise SystemExit("Faltan ELEVENLABS_API_KEY o ELEVENLABS_VOICE_ID")

    # Lee texto narrable (mismo extractor que el pipeline)
    if in_path.suffix == ".html":
        text = subprocess.check_output(["python3", "tools/extract_text.py", str(in_path)]).decode().strip()
    else:
        text = in_path.read_text(encoding="utf-8").strip()

    chunks = split_text(text)
    print(f"Texto: {len(text)} chars, {len(chunks)} chunk(s):")
    for i, c in enumerate(chunks, 1):
        print(f"  chunk {i}: {len(c)} chars")

    work = out_mp3.parent / ".gen_work"
    work.mkdir(parents=True, exist_ok=True)
    pieces, all_words, cum_offset = [], [], 0.0

    for i, ck in enumerate(chunks):
        prev_text = chunks[i - 1] if i > 0 else ""
        next_text = chunks[i + 1] if i + 1 < len(chunks) else ""
        print(f"\n[{i+1}/{len(chunks)}] sintetizando {len(ck)} chars...")
        resp = tts(ck, voice_id, api_key, model, prev_text=prev_text, next_text=next_text)
        audio = base64.b64decode(resp["audio_base64"])
        align = resp["alignment"]
        words = chars_to_words(
            align["characters"],
            align["character_start_times_seconds"],
            align["character_end_times_seconds"],
        )
        raw = work / f"chunk_{i:02d}.raw.mp3"
        nrm = work / f"chunk_{i:02d}.mp3"
        raw.write_bytes(audio)
        ffmpeg_normalize(raw, nrm)
        dur = ffprobe_duration(nrm)
        pieces.append(nrm)
        # Descartar «palabras» que son solo puntuación (— · «» «…» etc.).
        # ElevenLabs las devuelve como items del alignment aunque no llevan
        # ninguna letra, y inject_word_spans (que envuelve con \w+) no las
        # detecta en el HTML, generando un desfase artificial. Fix del
        # pipeline: si el token no contiene ningún carácter alfabético o
        # numérico, se salta.
        for w in words:
            if not re.search(r'\w', w["text"]):
                continue
            all_words.append({
                "i": len(all_words),
                "t": w["text"],
                "s": round(w["start"] + cum_offset, 3),
                "e": round(w["end"] + cum_offset, 3),
            })
        cum_offset += dur
        print(f"  {dur:.2f}s, palabras: {len(words)}, total: {cum_offset:.2f}s / {len(all_words)} palabras")

    ffmpeg_concat(pieces, out_mp3)
    final_dur = ffprobe_duration(out_mp3)

    if out_align:
        out = {
            "duration_seconds": final_dur,
            "word_count": len(all_words),
            "words": all_words,
        }
        out_align.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))

    # Limpieza
    for p in pieces:
        try: p.unlink()
        except: pass
    for raw in work.glob("*.raw.mp3"):
        try: raw.unlink()
        except: pass
    try: work.rmdir()
    except: pass

    print()
    print(f"OK: {out_mp3} ({out_mp3.stat().st_size // 1024} KB, {final_dur:.1f}s)")
    if out_align:
        print(f"OK: {out_align} ({len(all_words)} palabras)")


if __name__ == "__main__":
    main()
