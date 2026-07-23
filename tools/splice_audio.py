#!/usr/bin/env python3
"""Empalma un fragmento de audio nuevo dentro de un mp3 existente, usando
ElevenLabs /with-timestamps para sintetizar el fragmento y ffmpeg para
cortar+concatenar.

Reemplaza un rango contiguo de palabras [old_start, old_end) del alignment
viejo por el texto del fragmento nuevo. El corte se hace en los timestamps
exactos (end de la palabra anterior intacta, start de la siguiente).

Uso:
  splice_audio.py <plan.json>

plan.json debe tener:
  old_start_idx, old_end_idx, new_fragment_text,
  cut_start_seconds, cut_end_seconds,
  previous_text, next_text,
  in_mp3, in_alignment, out_mp3, out_alignment
"""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path


def tts(text, voice_id, api_key, model, prev_text="", next_text="", voice_settings=None):
    body = {
        "text": text,
        "model_id": model,
        "voice_settings": voice_settings or {
            "stability": 0.65,
            "similarity_boost": 0.75,
            "style": 0.20,
            "use_speaker_boost": True,
        },
    }
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
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


def ffmpeg_probe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]).decode().strip()
    return float(out)


def ffmpeg_extract(src, t_start, t_end, dst):
    """Cortar [t_start, t_end] de src → dst, re-encoding a mp3 para precisión."""
    args = ["ffmpeg", "-y", "-i", str(src), "-ss", f"{t_start:.3f}"]
    if t_end is not None:
        args += ["-to", f"{t_end:.3f}"]
    args += ["-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "1", str(dst)]
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ffmpeg_concat(parts, dst):
    """Concatenar mp3s con concat demuxer.

    Importante: el concat demuxer de ffmpeg interpreta las rutas del
    archivo de lista como RELATIVAS al directorio de la lista. Por eso
    forzamos paths absolutos resueltos antes de escribirlos, evitando
    el bug «No such file or directory» que ya nos quemó una vez.
    """
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
    if len(sys.argv) != 2:
        raise SystemExit("uso: splice_audio.py <plan.json>")
    plan = json.loads(Path(sys.argv[1]).read_text())

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
    if not api_key or not voice_id:
        raise SystemExit("Faltan ELEVENLABS_API_KEY o ELEVENLABS_VOICE_ID")

    in_mp3 = Path(plan["in_mp3"])
    in_align = Path(plan["in_alignment"])
    out_mp3 = Path(plan["out_mp3"])
    out_align = Path(plan["out_alignment"])
    work = out_mp3.parent / ".splice_work"
    work.mkdir(parents=True, exist_ok=True)

    # 1. TTS del fragmento nuevo
    fragment_text = plan["new_fragment_text"]
    print(f"Sintetizando fragmento: {len(fragment_text)} chars...")
    vs = plan.get("voice_settings")
    if vs:
        print(f"  voice_settings override: {vs}")
    resp = tts(fragment_text, voice_id, api_key, model,
               prev_text=plan.get("previous_text", ""),
               next_text=plan.get("next_text", ""),
               voice_settings=vs)
    frag_audio = base64.b64decode(resp["audio_base64"])
    align = resp["alignment"]
    frag_words = chars_to_words(
        align["characters"],
        align["character_start_times_seconds"],
        align["character_end_times_seconds"],
    )
    frag_mp3 = work / "fragment.mp3"
    frag_mp3.write_bytes(frag_audio)
    # re-empacar para tener bitrate consistente con los cortes
    frag_norm = work / "fragment-norm.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(frag_mp3), "-c:a", "libmp3lame",
         "-b:a", "128k", "-ar", "44100", "-ac", "1", str(frag_norm)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    frag_duration = ffmpeg_probe_duration(frag_norm)
    print(f"  audio fragmento: {frag_duration:.3f}s, palabras: {len(frag_words)}")

    # 2. cortar prefix y suffix del audio viejo
    t_start = plan["cut_start_seconds"]
    t_end = plan["cut_end_seconds"]
    prefix = work / "prefix.mp3"
    suffix = work / "suffix.mp3"
    has_prefix = t_start > 0.05  # reemplazo al inicio del audio → sin prefix
    print(f"Cortando prefix [0, {t_start:.3f}] y suffix [{t_end:.3f}, end]...")
    if has_prefix:
        ffmpeg_extract(in_mp3, 0.0, t_start, prefix)
    ffmpeg_extract(in_mp3, t_end, None, suffix)

    # 3. concatenar
    print("Concatenando prefix + fragmento + suffix...")
    parts = ([prefix.resolve()] if has_prefix else []) + [frag_norm.resolve(), suffix.resolve()]
    ffmpeg_concat(parts, out_mp3)
    new_duration = ffmpeg_probe_duration(out_mp3)
    print(f"  audio final: {new_duration:.3f}s "
          f"(viejo: {plan['old_duration_seconds']:.3f}s)")

    # 4. reconstruir alignment
    old_align = json.loads(in_align.read_text())
    old_words = old_align["words"]
    start_idx = plan["old_start_idx"]
    end_idx = plan["old_end_idx"]

    # tiempos: prefix dura ~t_start (con cierta precisión de ffmpeg)
    prefix_duration = ffmpeg_probe_duration(prefix) if has_prefix else 0.0
    suffix_duration = ffmpeg_probe_duration(suffix)
    # offset para las palabras del fragmento: empiezan al final del prefix
    frag_offset = prefix_duration
    # offset para las palabras del suffix viejo: empiezan al final del fragmento
    suffix_offset = prefix_duration + frag_duration

    new_words = []
    # prefijo intacto
    for w in old_words[:start_idx]:
        new_words.append(w)
    # fragmento
    for w in frag_words:
        new_words.append({
            "i": -1,  # se reasigna abajo
            "t": w["text"],
            "s": round(w["start"] + frag_offset, 3),
            "e": round(w["end"] + frag_offset, 3),
        })
    # sufijo intacto, con offset = suffix_offset - t_end (donde empezaba antes)
    delta = suffix_offset - t_end
    for w in old_words[end_idx:]:
        new_words.append({
            "i": -1,
            "t": w["t"],
            "s": round(w["s"] + delta, 3),
            "e": round(w["e"] + delta, 3),
        })
    # reasignar índices
    for i, w in enumerate(new_words):
        w["i"] = i

    out = {
        "duration_seconds": new_duration,
        "word_count": len(new_words),
        "words": new_words,
    }
    out_align.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"OK: {out_mp3} ({out_mp3.stat().st_size // 1024} KB, {new_duration:.1f}s)")
    print(f"OK: {out_align} ({len(new_words)} palabras)")
    print()
    print("Sanity check de las costuras:")
    if start_idx >= 1:
        wb = new_words[start_idx - 1]
        wn = new_words[start_idx]
        print(f"  antes:  '{wb['t']}' end={wb['e']:.3f}")
        print(f"  empate: '{wn['t']}' start={wn['s']:.3f}  (gap {wn['s']-wb['e']:.3f}s)")
    end_in_new = start_idx + len(frag_words)
    if end_in_new < len(new_words):
        wb = new_words[end_in_new - 1]
        wn = new_words[end_in_new]
        print(f"  antes:  '{wb['t']}' end={wb['e']:.3f}")
        print(f"  empate: '{wn['t']}' start={wn['s']:.3f}  (gap {wn['s']-wb['e']:.3f}s)")


if __name__ == "__main__":
    main()
