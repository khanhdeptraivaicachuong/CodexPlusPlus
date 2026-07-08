import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "tools/i18n-export.json").read_text(encoding="utf-8"))
CACHE_PATH = ROOT / "tools/i18n-vi-cache.json"
cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(""", "\"").replace("
", "
").replace("", "")

def vi(en: str) -> str:
    return cache.get(en, en)

def block(name: str, mapping: dict) -> str:
    lines = [f"export const {name}: Record<string, string> = {{"]
    for zh, en in mapping.items():
        lines.append(f"  "{esc(zh)}": "{esc(vi(en))}",")
    lines.append("};")
    return "
".join(lines)

parts = [
    "// Vietnamese UI. Refresh: python tools/gen-i18n-vi.py then python tools/build_i18n_vi.py
",
    block("VI_PLAIN", DATA["plain"]),
    block("VI_TEMPLATE", DATA["template"]),
    block("VI_BACKEND", DATA["backend"]),
    "export const VI_BACKEND_PATTERNS: Array<[RegExp, string]> = [",
]
for src, en_rep in DATA["patterns"]:
    parts.append(f"  [new RegExp({json.dumps(src)}), {json.dumps(vi(en_rep))}],")
parts.append("];
")
out = ROOT / "apps/codex-plus-manager/src/i18n-vi.ts"
out.write_text("

".join(parts), encoding="utf-8")
hit = sum(1 for en in DATA["plain"].values() if en in cache)
print(out, "cache", len(cache), "plain_vi", hit, "/", len(DATA["plain"]))
