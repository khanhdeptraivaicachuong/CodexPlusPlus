import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const exportPath = path.join(root, "tools/i18n-export.json");
const cachePath = path.join(root, "tools/i18n-vi-cache.json");
const outPath = path.join(root, "apps/codex-plus-manager/src/i18n-vi.ts");
const data = JSON.parse(fs.readFileSync(exportPath, "utf8"));
const cache = fs.existsSync(cachePath) ? JSON.parse(fs.readFileSync(cachePath, "utf8")) : {};
function esc(s){return s.replaceAll("\\","\\\\").replaceAll("\"","\\\"").replaceAll("
","\n").replaceAll("","");}
function viFromEn(en){return cache[en]??en;}
function emitRecord(name,zhToEn){const lines=[`export const ${name}: Record<string, string> = {`];for(const[zh,en]of Object.entries(zhToEn))lines.push(`  "${esc(zh)}": "${esc(viFromEn(en))}",`);lines.push("};");return lines.join("
");}
const patLines=["export const VI_BACKEND_PATTERNS: Array<[RegExp, string]> = ["];
for(const[src,enRep]of data.patterns)patLines.push(`  [new RegExp(${JSON.stringify(src)}), ${JSON.stringify(viFromEn(enRep))}],`);
patLines.push("];");
const body=[emitRecord("VI_PLAIN",data.plain),emitRecord("VI_TEMPLATE",data.template),emitRecord("VI_BACKEND",data.backend),patLines.join("
")].join("

");
fs.writeFileSync(outPath,"// Vietnamese UI

"+body+"
");
const hit=Object.values(data.plain).filter(en=>cache[en]).length;
console.log("wrote",outPath,hit,Object.keys(data.plain).length);