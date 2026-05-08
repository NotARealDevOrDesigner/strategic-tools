# 4U-Analyse-Pipeline

Eine Python-basierte Multi-Agent-Analyse-Pipeline zur Validierung von Geschäftsproblemen nach dem **4U-Framework** von Michael Skok.

## Überblick

Die Pipeline analysiert ein Problem automatisiert entlang vier strategischer Dimensionen:

1. **UNWORKABLE** – Das aktuelle System funktioniert nicht mehr
2. **UNAVOIDABLE** – Externe Kräfte erzwingen die Veränderung
3. **URGENT** – Es gibt zeitliche Dringlichkeit
4. **UNDERSERVED** – Kundengruppen sind nicht bedient

Nach diesen vier Analysen erstellt die Pipeline eine **Synthese** mit Gesamtbewertung.

## Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Optional: .env-Datei für lokale Entwicklung erstellen
cp .env.example .env
# Füge deinen OpenAI API-Schlüssel in .env hinzu (wird nicht committed)
```

## Verwendung

### Web-UI (empfohlen für Anfänger)

```bash
python app.py
```

Öffne deinen Browser und gehe zu `http://localhost:8000`. Gib deinen OpenAI API-Schlüssel und das Problem ein, das du analysieren möchtest.

### CLI-Modus

```bash
python main.py "Wir haben Schwierigkeiten mit manueller Rechnungsstellung" "sk-your-openai-api-key"
```

Oder interaktiv:

```bash
python main.py
# → Prompt fragt nach dem Problem und API-Schlüssel
```

## Architektur

### Separation of Concerns

Die Pipeline ist in vier unabhängige Module aufgeteilt:

```
agents/
  └── analyse_agent.py      # Low-level Agent-Runner (keine Geschäftslogik)

## Architektur

### Separation of Concerns

Die Pipeline ist in vier unabhängige Module aufgeteilt:

```

agents/
└── analyse_agent.py # Low-level Agent-Runner (keine Geschäftslogik) # - Nur API-Calls zu Claude # - Rückgabe: rohe Text-Responses

methods/
└── 4u_method.py # High-level Analyse-Logik # - Orchestriert die vier Dimensionen # - Kombiniert Agent + Prompts # - Gibt strukturiertes Output-Dict zurück

prompts/
└── 4u_prompts.py # Alle Textdaten & Templates # - SYSTEM_PROMPT (Agenten-Persona) # - STEP_PROMPTS (dict mit 4 Dimensionen) # - SYNTHESE_PROMPT # - KEINE Hardcoding von Geschäftslogik

main.py # CLI & Orchestrierung # - Nimmt Problem als Input # - Startet FourUMethod # - Formatiert Output

```

### Warum diese Struktur?

- **Wiederverwendbarkeit:** Der `AnalyseAgent` kann für jede neue Methode verwendet werden
- **Wartbarkeit:** Prompts sind zentralisiert in `prompts/`
- **Erweiterbarkeit:** Neue Methoden (z.B. Jobs-to-be-Done) können als neue Datei in `methods/` + `prompts/` hinzugefügt werden, ohne `agents/` zu berühren

## Beispiel-Output

```

==================================================
4U-ANALYSE: Manuelle Rechnungsstellung
==================================================

[Agent 1/4] UNWORKABLE
→ Analysiere... ✓
[UNWORKABLE] Signal: Stark
Viele Fehler bei manueller Dateneingabe, zeitaufwändig, fehleranfällig...

[Agent 2/4] UNAVOIDABLE
→ Analysiere... ✓
[UNAVOIDABLE] Signal: Mittel
Regulierung XYZ verlangt digitale Nachverfolgung ab Q4 2026...

[Agent 3/4] URGENT
→ Analysiere... ✓
[URGENT] Signal: Schwach
Konkurrenten automatisieren bereits, aber Timeline unklar...

[Agent 4/4] UNDERSERVED
→ Analysiere... ✓
[UNDERSERVED] Signal: Stark
Mittelständische Unternehmen brauchen einfache, günstige Lösung...

==================================================
SYNTHESE & VALIDIERUNG
==================================================

TABELLARISCHE ÜBERSICHT:

- UNWORKABLE: Stark
- UNAVOIDABLE: Mittel
- URGENT: Schwach
- UNDERSERVED: Stark

STÄRKSTE SIGNALE:

- Manuelle Prozesse schlagen fehl (Unworkable)
- Große unterversorgte Kundengruppe (Underserved)

WISSENSLÜCKEN & RISIKEN:

- Regulierungs-Timeline unklar
- Konkurrenzlandschaft nicht vollständig erhoben

GESAMTBEWERTUNG:
Teilweise – Problem hat starke Unworkable- und Underserved-Signale, aber
Urgency und regulatorische Drivers sind noch nicht vollständig validiert.

==================================================

````

## Erweiterung: Neue Methode hinzufügen

Beispiel: **Jobs-to-be-Done-Framework**

1. **Erstelle neue Prompt-Datei:**

```bash
touch prompts/jtbd_prompts.py
````

2. **Schreibe SYSTEM_PROMPT und STEP_PROMPTS** in `jtbd_prompts.py`

3. **Erstelle neue Methode-Klasse:**

```bash
touch methods/jtbd_method.py
# Importiere AnalyseAgent, schreibe JobsToBeDoneMethod-Klasse
```

4. **Agent-Code bleibt UNVERÄNDERT!**

## Modell

- **Claude Sonnet 4** (claude-sonnet-4-20250514)
- **Max Tokens:** 1024 pro Call (anpassbar in `analyse_agent.py`)

## Abhängigkeiten

- `anthropic` – Anthropic Python SDK
- `python-dotenv` – Umgebungsvariablen aus .env laden

## Fehlerbehandlung

- Fehlende API-Key → Clear Error-Message
- API-Fehler → Exception mit Details
- Ungültiges Problem → Validation vor Analyse

## Nächste Schritte

- [ ] Persistierung der Ergebnisse (JSON/CSV)
- [ ] Batch-Analysen (mehrere Probleme gleichzeitig)
- [ ] Web-UI mit FastAPI
- [ ] Zusätzliche Frameworks (JTBD, Value Proposition Canvas, etc.)
- [ ] Integration mit Notion/Confluence für Dokumentation
