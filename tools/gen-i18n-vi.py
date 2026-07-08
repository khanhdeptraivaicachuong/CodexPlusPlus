#!/usr/bin/env python3
"""Generate i18n-vi.ts from tools/i18n-export.json (EN values -> VI)."""
import json, time
from pathlib import Path
from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "tools" / "i18n-export.json"
OUT = ROOT / "apps" / "codex-plus-manager" / "src" / "i18n-vi.ts"
CACHE = ROOT / "tools" / "i18n-vi-cache.json"
SLEEP = 0.35

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\n").replace("\r", "")

def translate_map(tr, mapping, cache):
    out = {}
    items = list(mapping.items())
    for i, (zh_key, en_val) in enumerate(items):
        if en_val in cache:
            out[zh_key] = cache[en_val]
            continue
        try:
            vi = tr.translate(en_val)
            cache[en_val] = vi
            out[zh_key] = vi
        except Exception as e:
            print("fail", i, repr(e))
            out[zh_key] = en_val
            cache[en_val] = en_val
        if (i + 1) % 10 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(i + 1, "/", len(items))
        time.sleep(SLEEP)
    return out

def emit_record(name, mapping):
    lines = ["export const %s: Record<string, string> = {" % name]
    for k, v in mapping.items():
        lines.append('  "%s": "%s",' % (esc(k), esc(v)))
    lines.append("};")
    return "\n".join(lines)

def main():
    data = json.loads(EXPORT.read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    tr = GoogleTranslator(source="en", target="vi")
    vi_plain = translate_map(tr, data["plain"], cache)
    vi_template = translate_map(tr, data["template"], cache)
    vi_backend = translate_map(tr, data["backend"], cache)
    vi_patterns = []
    for src, en_rep in data["patterns"]:
        if en_rep in cache:
            vi_rep = cache[en_rep]
        else:
            try:
                vi_rep = tr.translate(en_rep)
                cache[en_rep] = vi_rep
            except Exception:
                vi_rep = en_rep
            time.sleep(SLEEP)
        vi_patterns.append((src, vi_rep))
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    header = "// Vietnamese translations for Codex++ manager UI (tools/gen-i18n-vi.py)\n\n"
    parts = [emit_record("VI_PLAIN", vi_plain), emit_record("VI_TEMPLATE", vi_template), emit_record("VI_BACKEND", vi_backend)]
    pat_lines = ["export const VI_BACKEND_PATTERNS: Array<[RegExp, string]> = ["]
    for src, vi_rep in vi_patterns:
        pat_lines.append("  [new RegExp(%s), %s]," % (json.dumps(src), json.dumps(vi_rep)))
    pat_lines.append("];")
    OUT.write_text(header + "\n\n".join(parts) + "\n\n" + "\n".join(pat_lines) + "\n", encoding="utf-8")
    print("wrote", OUT)

if __name__ == "__main__":
    main()
