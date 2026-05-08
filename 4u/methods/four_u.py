from agents.analyse_agent import AnalyseAgent
from prompts.four_u_prompts import SYSTEM_PROMPT, STEP_PROMPTS, SYNTHESE_PROMPT
import json


class FourUMethod:
    """Implementierung der 4U-Analyse-Methode."""

    def __init__(self, api_key: str):
        """Initialisiere den Agent."""
        self.agent = AnalyseAgent(api_key)
        self.results = {}

    def run(self, problem: str) -> dict:
        """
        Führe die 4U-Analyse durch.

        Args:
            problem: Das zu analysierende Problem

        Returns:
            Dict mit keys: unworkable, unavoidable, urgent, underserved, synthese
        """
        print(f"\n{'━' * 50}")
        print(f"4U-ANALYSE: {problem[:50]}..." if len(problem) > 50 else f"4U-ANALYSE: {problem}")
        print(f"{'━' * 50}\n")

        # Dimensionen sequenziell analysieren
        dimensions = [
            ("unworkable", "UNWORKABLE", 1),
            ("unavoidable", "UNAVOIDABLE", 2),
            ("urgent", "URGENT", 3),
            ("underserved", "UNDERSERVED", 4),
        ]

        for key, label, step_num in dimensions:
            print(f"[Agent {step_num}/4] {label}")

            # User-Prompt mit Problem formatieren
            user_prompt = STEP_PROMPTS[key].format(problem=problem)

            # Agent aufrufen
            result = self.agent.run(step_name=label, system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)

            # Ergebnis speichern
            self.results[key] = result

            # Ergebnis in Konsole ausgeben (mit Parsing des Signals)
            self._print_result(label, result)
            print()

    def run_step(self, problem: str, dimension: str) -> dict:
        """
        Führe einen einzelnen Analyse-Schritt durch.

        Args:
            problem: Das zu analysierende Problem
            dimension: Die Dimension ('unworkable', 'unavoidable', 'urgent', 'underserved')

        Returns:
            Dict mit Analyse-Ergebnis
        """
        self._problem = problem  # Store problem for synthese

        labels = {
            "unworkable": ("UNWORKABLE", 1),
            "unavoidable": ("UNAVOIDABLE", 2),
            "urgent": ("URGENT", 3),
            "underserved": ("UNDERSERVED", 4),
        }

        label, step_num = labels[dimension]

        print(f"[Agent {step_num}/4] {label}")

        # User-Prompt mit Problem formatieren
        user_prompt = STEP_PROMPTS[dimension].replace("{problem}", problem)

        # Agent aufrufen
        result = self.agent.run(step_name=label, system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)

        # Ergebnis speichern
        self.results[dimension] = result

        # Ergebnis in Konsole ausgeben
        self._print_result(label, result)

        return result

    def run_synthese(self) -> dict:
        """
        Führe die Synthese durch.

        Returns:
            Dict mit Synthese-Ergebnis
        """
        problem = self._problem

        print(f"{'━' * 50}")
        print("SYNTHESE & VALIDIERUNG")
        print(f"{'━' * 50}")

        synthese_prompt = SYNTHESE_PROMPT.replace(
            "{problem}", problem
        ).replace(
            "{unworkable}", json.dumps(self.results["unworkable"], ensure_ascii=False)
        ).replace(
            "{unavoidable}", json.dumps(self.results["unavoidable"], ensure_ascii=False)
        ).replace(
            "{urgent}", json.dumps(self.results["urgent"], ensure_ascii=False)
        ).replace(
            "{underserved}", json.dumps(self.results["underserved"], ensure_ascii=False)
        )

        synthese_result = self.agent.run(
            step_name="SYNTHESE",
            system_prompt=SYSTEM_PROMPT,
            user_prompt=synthese_prompt
        )

        self.results["synthese"] = synthese_result
        print("\n" + json.dumps(synthese_result, ensure_ascii=False, indent=2))
        print(f"\n{'━' * 50}\n")

        return synthese_result

    def _print_result(self, label: str, result: dict) -> None:
        """Formatierte Ausgabe eines Analyseergebnisses."""
        # result ist jetzt ein dict mit: analysis, sources, assumptions, counter_arguments, signal
        analysis_text = result.get("analysis", "N/A")
        signal = result.get("signal", "Unbekannt")

        # Truncate für Anzeige (max 300 Zeichen)
        preview = analysis_text[:300] + "..." if len(analysis_text) > 300 else analysis_text

        print(f"  [{label}] Signal: {signal}")
        print(f"  {preview}\n")
