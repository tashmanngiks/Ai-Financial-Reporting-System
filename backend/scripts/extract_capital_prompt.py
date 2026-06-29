from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / "frontend/src/constants/reportPrompts.ts").read_text(encoding="utf-8")
marker = "export const CAPITAL_ADEQUACY_CRIPE_PROMPT = `"
start = text.index(marker) + len(marker)
end_marker = "\n\nexport const REPORT_PROMPT_TEMPLATES"
end = text.index(end_marker, start)
content = text[start:end].replace("\\'", "'")
out = ROOT / "backend/analytics/data/capital_adequacy_cripe_prompt.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(content, encoding="utf-8")
print(f"wrote {len(content)} chars to {out}")
