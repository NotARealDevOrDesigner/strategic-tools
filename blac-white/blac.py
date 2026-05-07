#!/usr/bin/env python3
"""BLAC & White — Throwaway Prototype
Depth: quick (~2k tokens) | standard (~4k) | deep (~6k)
"""

import anthropic
import json
import argparse
import sys

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"

# ── Agent 1: Analyse ──────────────────────────────────────────────────────────

A1_ROLE = (
    "Du bist ein strategischer Analyst nach dem BLAC & White Framework (Michael Skok, Harvard Innovation Lab). "
    "Bewerte Probleme anhand Sichtbarkeit, Kritikalität und White Space. Antworte NUR mit validem JSON."
)

def a1_sections(depth: str) -> str:
    s = """
SEKTION A — SICHTBARKEIT (Score 1-10, 1=Latent, 10=Blatant):
- 3-5 beobachtbare Symptome im Alltag des Zielkunden
- Awareness-Level 0-4 (0=unbewusst … 4=dringend) + 1-2 Marktsignale
- Missionary-Selling-Risiko: niedrig|mittel|hoch"""
    if depth != "quick":
        s += "\n- Trigger-Events die latentes Problem blatant machen könnten (regulatorisch/technologisch/wirtschaftlich)"

    s += """

SEKTION B — KRITIKALITÄT (Score 1-10, 1=Aspirational, 10=Critical):
- Konsequenzen bei Nichthandeln (operativ, finanziell, rechtlich)
- Wer-wird-gefeuert-Test: ja|nein
- Budget-Priorität: Top-3-Ausgabe? Wer entscheidet?"""
    if depth != "quick":
        s += "\n- Regulatorischer Zwang: Compliance-Deadlines oder Strafen vorhanden?"

    s += """

SEKTION C — WHITE SPACE (Score 1-10, 1=überfüllt, 10=offen):
- Direkte + indirekte Wettbewerber; haben Incumbents Dis-Incentive zur Lösung?
- Lücken: funktional, Segment, Erlebnis
- Timing: zu früh|richtig|zu spät — wie lange bleibt Fenster offen?"""

    if depth == "deep":
        s += "\n- Verteidigbarkeit: technologische Moats, Switching Costs, Zeit bis Nachahmer"

    s += """

SEKTION D — QUADRANT:
Q1=Latent/Aspirational | Q2=Blatant/Aspirational | Q3=Blatant/Critical (Sweet Spot) | Q4=Latent/Critical
- Quadrant aus A+B bestimmen"""
    if depth != "quick":
        s += "\n- Segment-Vergleich: welches Segment ist nächsten an Q3?"
    s += "\n- MVS-Empfehlung (Minimum Viable Segment)"

    schema = """

OUTPUT — NUR JSON (kein Text davor/danach):
{
  scores: {visibility: int, criticality: int, white_space: int},
  quadrant: "Q1"|"Q2"|"Q3"|"Q4",
  quadrant_label: str,
  confidence: "low"|"medium"|"high",
  key_findings: {visibility: str, criticality: str, white_space: str},
  mvs: str"""

    if depth != "quick":
        schema += """,
  segments: [{name: str, quadrant: str, visibility: int, criticality: int, mvs_priority: int}],
  triggers: [str],
  risks: [str]"""

    if depth == "deep":
        schema += """,
  competitor_analysis: str"""

    schema += "\n}"
    return s + schema


# ── Agent 2: Strategie ────────────────────────────────────────────────────────

A2_ROLE = (
    "Du bist ein strategischer Berater. Leite aus einer BLAC-Analyse konkrete Handlungsempfehlungen ab. "
    "Antworte NUR mit validem JSON."
)

def a2_sections(depth: str) -> str:
    s = """
SEKTION A — BLAC MOVES (nur wenn aktueller Quadrant ≠ Q3):
Ist→Ziel-Quadrant. Migrations-Hebel:
- Latent→Blatant: Thought Leadership, Demo erlebbar machen, Community
- Aspirational→Critical: Regulierung nutzen, Kosten des Nichthandelns quantifizieren, Segment wechseln"""

    if depth == "quick":
        s += "\nPhase 1 (0-3 Mo): Top-3 Quick Wins + Messmeilenstein"
    else:
        s += """
Phasen:
  Phase 1 (0-3 Mo): Quick Wins + Meilenstein
  Phase 2 (3-9 Mo): Fundament + Meilenstein
  Phase 3 (9-18 Mo): Skalierung + Meilenstein"""

    s += """

SEKTION B — GO / NO-GO:
GO: Q3 + White Space ≥6
CONDITIONAL_GO: realistischer Migrationspfad vorhanden
PIVOT: anderes Segment liegt näher an Q3
NO_GO: Latent/Aspirational ohne erkennbaren Pfad"""

    if depth in ("standard", "deep"):
        s += """

SEKTION C — FRAMEWORK-BRÜCKE:
- 4U: Unworkable/Unavoidable/Urgent/Underserved (true/false)
- 3D: Discontinuous/Defensible/Disruptive (true/false)
- Gain/Pain-Ratio: hoch|mittel|niedrig
- Value Prop (Template): "Für [MVS] die unzufrieden sind mit [Status quo], ist [Produkt] ein [Kategorie] das [Capability] bietet — im Gegensatz zu [Wettbewerb].\""""

    schema = """

OUTPUT — NUR JSON:
{
  decision: "GO"|"CONDITIONAL_GO"|"PIVOT"|"NO_GO",
  decision_rationale: str,
  current_quadrant: str,
  target_quadrant: str,
  mvs: str,
  moves: [{phase: int, timeframe: str, actions: [str], milestone: str}]"""

    if depth in ("standard", "deep"):
        schema += """,
  frameworks: {
    four_u: {unworkable: bool, unavoidable: bool, urgent: bool, underserved: bool},
    three_d: {discontinuous: bool, defensible: bool, disruptive: bool},
    gain_pain_ratio: str
  },
  value_proposition: str"""

    if depth == "deep":
        schema += """,
  roadmap_summary: str"""

    schema += "\n}"
    return s + schema


# ── Agent 3: Markdown Report ──────────────────────────────────────────────────

A3_SYSTEM = (
    "Du bist ein Report-Formatter. Wandle BLAC-Analysedaten in einen strukturierten Markdown-Report um. "
    "Schreibe direkt ohne Einleitungsformeln."
)

def a3_user(analysis: dict, strategy: dict, depth: str) -> str:
    detail = "kurz und prägnant (max. 1 Seite)" if depth == "quick" else "detailliert mit Begründungen"
    extra_sections = ""
    if depth != "quick":
        extra_sections += "\n## Roadmap"
    if depth == "deep":
        extra_sections += "\n## Framework-Check (4U / 3D)"

    return f"""Erstelle einen {detail}en Markdown-Report.

ANALYSE:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

STRATEGIE:
{json.dumps(strategy, ensure_ascii=False, indent=2)}

Struktur:
# BLAC & White Analyse
## Executive Summary
## Scores & Quadrant
## Key Findings
## Strategische Empfehlung{extra_sections}"""


# ── Agent Calls ───────────────────────────────────────────────────────────────

import re as _re

def _extract_json_object(text: str) -> str:
    """Extract first complete JSON object from text, even with trailing content."""
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_str:
            escape = True
            continue
        if ch == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def _clean_json(text: str) -> str:
    """Fix common model JSON issues: trailing commas, JS comments."""
    # Remove single-line JS comments
    text = _re.sub(r'//[^\n]*', '', text)
    # Remove trailing commas before } or ]
    text = _re.sub(r',(\s*[}\]])', r'\1', text)
    return text


def _parse_json(text: str) -> dict:
    text = text.strip()
    # Strip markdown fences
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Extract first JSON object (handles trailing text)
    candidate = _extract_json_object(text)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    # Clean common issues and retry
    cleaned = _clean_json(candidate)
    return json.loads(cleaned)


def run_agent1(user_input: dict, depth: str) -> dict:
    max_tok = {"quick": 800, "standard": 1400, "deep": 2000}[depth]
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        system=[
            {"type": "text", "text": A1_ROLE, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": a1_sections(depth), "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": json.dumps(user_input, ensure_ascii=False)}],
    )
    return _parse_json(resp.content[0].text)


def run_agent2(analysis: dict, depth: str) -> dict:
    max_tok = {"quick": 600, "standard": 1200, "deep": 1800}[depth]
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        system=[
            {"type": "text", "text": A2_ROLE, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": a2_sections(depth), "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": json.dumps(analysis, ensure_ascii=False)}],
    )
    return _parse_json(resp.content[0].text)


def run_agent3(analysis: dict, strategy: dict, depth: str) -> str:
    max_tok = {"quick": 600, "standard": 1400, "deep": 2200}[depth]
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        system=[{"type": "text", "text": A3_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": a3_user(analysis, strategy, depth)}],
    )
    return resp.content[0].text


# ── Memory Mode (kurze Prompts — nutzt Claudes eingebautes BLAC-Wissen) ──────

A1_ROLE_MEM = (
    "Analysiere nach BLAC & White (Michael Skok, Harvard). "
    "Scores Sichtbarkeit/Kritikalität/White Space 1-10, Quadrant Q1-Q4. "
    "Antworte NUR mit validem JSON: alle Keys und Strings in doppelten Anführungszeichen, keine Kommentare, kein Text vor oder nach dem JSON."
)

_MEM_A1_SCHEMA = """{
  "scores": {"visibility": 7, "criticality": 8, "white_space": 5},
  "quadrant": "Q3",
  "quadrant_label": "Blatant / Critical",
  "confidence": "high",
  "key_findings": {"visibility": "...", "criticality": "...", "white_space": "..."},
  "mvs": "..."
}"""

A2_ROLE_MEM = (
    "Leite BLAC-Strategie aus der Analyse ab. "
    "Entscheide GO/CONDITIONAL_GO/PIVOT/NO_GO. "
    "Antworte NUR mit validem JSON: alle Keys und Strings in doppelten Anführungszeichen, keine Kommentare, kein Text vor oder nach dem JSON."
)

_MEM_A2_SCHEMA = """{
  "decision": "GO",
  "decision_rationale": "...",
  "current_quadrant": "Q3",
  "target_quadrant": "Q3",
  "mvs": "...",
  "moves": [{"phase": 1, "timeframe": "0-3 Mo", "actions": ["..."], "milestone": "..."}]
}"""


def run_agent1_mem(user_input: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=A1_ROLE_MEM,
        messages=[{"role": "user", "content": json.dumps(user_input, ensure_ascii=False) + f"\n\nSchema:\n{_MEM_A1_SCHEMA}"}],
    )
    return _parse_json(resp.content[0].text)


def run_agent2_mem(analysis: dict) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=A2_ROLE_MEM,
        messages=[{"role": "user", "content": json.dumps(analysis, ensure_ascii=False) + f"\n\nSchema:\n{_MEM_A2_SCHEMA}"}],
    )
    return _parse_json(resp.content[0].text)


def run_agent3_mem(analysis: dict, strategy: dict) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1100,
        system="Kurzer BLAC-Markdown-Report. Kein Intro.",
        messages=[{"role": "user", "content": (
            f"Analyse:\n{json.dumps(analysis, ensure_ascii=False)}\n\n"
            f"Strategie:\n{json.dumps(strategy, ensure_ascii=False)}\n\n"
            "Struktur:\n# BLAC Analyse\n## Summary\n## Scores & Quadrant\n## Empfehlung"
        )}],
    )
    return resp.content[0].text


# ── CLI ───────────────────────────────────────────────────────────────────────

EXAMPLE_INPUT = {
    "problem": "KMUs verlieren täglich Stunden durch manuelle Buchhaltung",
    "solution": "KI-gestützte Buchhaltungsautomatisierung für KMUs",
    "segments": ["KMU Dienstleistung", "Freiberufler", "E-Commerce KMU"],
    "industry": "FinTech / SaaS",
    "regions": ["DACH"],
    "stage": "MVP",
    "model": "B2B",
}


def main():
    parser = argparse.ArgumentParser(description="BLAC & White Analyse-Tool")
    parser.add_argument(
        "--depth",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Analysetiefe (default: standard)",
    )
    parser.add_argument("--input", help="Pfad zu JSON-Input-Datei (sonst: Beispiel-Input)")
    parser.add_argument("--out", help="Output-Datei (.md), sonst stdout")
    parser.add_argument("--json", action="store_true", help="Roh-JSON statt Markdown ausgeben")
    args = parser.parse_args()

    user_input = EXAMPLE_INPUT
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            user_input = json.load(f)

    print(f"[1/3] Analyse ({args.depth})...", file=sys.stderr)
    analysis = run_agent1(user_input, args.depth)

    print("[2/3] Strategie...", file=sys.stderr)
    strategy = run_agent2(analysis, args.depth)

    if args.json:
        output = json.dumps({"analysis": analysis, "strategy": strategy}, ensure_ascii=False, indent=2)
    else:
        print("[3/3] Report...", file=sys.stderr)
        output = run_agent3(analysis, strategy, args.depth)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Gespeichert: {args.out}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
