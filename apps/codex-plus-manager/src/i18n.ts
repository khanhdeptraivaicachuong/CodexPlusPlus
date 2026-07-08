// Lightweight source-text-keyed i18n for the Codex++ manager UI.
//
// The app is authored in Chinese. Every user-facing Chinese literal is wrapped
// with `t("中文")` (plain strings) or `tf("前缀 {0}", [expr])` (interpolated
// strings). Dictionaries: i18n-en.ts, i18n-vi.ts.
//
// Language is resolved once at module load. Switching language persists and
// reloads the webview so module-level literals re-evaluate.

import { EN_BACKEND, EN_BACKEND_PATTERNS, EN_PLAIN, EN_TEMPLATE } from "@/i18n-en";
import { VI_BACKEND, VI_BACKEND_PATTERNS, VI_PLAIN, VI_TEMPLATE } from "@/i18n-vi";

export type Language = "zh" | "en" | "vi";

const STORAGE_KEY = "codex-plus-lang";

function resolveInitialLanguage(): Language {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "en" || stored === "vi") return stored;
  } catch {
    // ignore
  }
  return "zh";
}

const LANG: Language = resolveInitialLanguage();

export function getLanguage(): Language {
  return LANG;
}

function translatePlain(zh: string): string {
  if (LANG === "zh") return zh;
  const plain = LANG === "en" ? EN_PLAIN[zh] ?? EN_BACKEND[zh] : VI_PLAIN[zh] ?? VI_BACKEND[zh];
  if (plain) return plain;
  const patterns = LANG === "en" ? EN_BACKEND_PATTERNS : VI_BACKEND_PATTERNS;
  for (const [re, replacement] of patterns) {
    if (re.test(zh)) return zh.replace(re, replacement);
  }
  return zh;
}

/** Translate a plain Chinese literal. Falls back to the source text. */
export function t(zh: string): string {
  return translatePlain(zh);
}

export function tf(key: string, args: Array<string | number>): string {
  const dict = LANG === "en" ? EN_TEMPLATE : LANG === "vi" ? VI_TEMPLATE : null;
  const template = dict ? dict[key] ?? key : key;
  return template.replace(/\{(\d+)\}/g, (match, index) => {
    const value = args[Number(index)];
    return value === undefined || value === null ? match : String(value);
  });
}

export function setLanguage(language: Language): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, language);
  } catch {
    // ignore
  }
  window.location.reload();
}

const LANG_CYCLE: Language[] = ["zh", "vi", "en"];

/** Cycle UI language: 中文 → Tiếng Việt → English. */
export function cycleLanguage(): void {
  const idx = LANG_CYCLE.indexOf(LANG);
  const next = LANG_CYCLE[(idx + 1) % LANG_CYCLE.length];
  setLanguage(next);
}

/** @deprecated Use cycleLanguage() */
export function toggleLanguage(): void {
  cycleLanguage();
}

export function languageButtonTitle(): string {
  if (LANG === "zh") return translatePlain("切换到越南语");
  if (LANG === "vi") return translatePlain("切换到英文");
  return translatePlain("切换到中文");
}
