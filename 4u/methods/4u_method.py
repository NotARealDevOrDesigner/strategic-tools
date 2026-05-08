from agents.analyse_agent import AnalyseAgent
from prompts.4u_prompts import SYSTEM_PROMPT, STEP_PROMPTS, SYNTHESE_PROMPT


class FourUMethod:
    """Implementierung der 4U-Analyse-Methode."""

    def __init__(self):
        """Initialisiere den Agent."""
        self.agent = AnalyseAgent()
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

        # Synthese-Schritt
        print(f"{'━' * 50}")
        print("SYNTHESE & VALIDIERUNG")
        print(f"{'━' * 50}")

        synthese_prompt = SYNTHESE_PROMPT.format(
            problem=problem,
            unworkable=self.results["unworkable"],
            unavoidable=self.results["unavoidable"],
            urgent=self.results["urgent"],
            underserved=self.results["underserved"]
        )

        synthese_result = self.agent.run(
            step_name="SYNTHESE",
            system_prompt=SYSTEM_PROMPT,
            user_prompt=synthese_prompt
        )

        self.results["synthese"] = synthese_result
        print("\n" + synthese_result)
        print(f"\n{'━' * 50}\n")

        return self.results

    def _print_result(self, label: str, result: str) -> None:
        """Formatierte Ausgabe eines Analyseergebnisses."""
        # Versuche Signal zu extrahieren
        signal = self._extract_signal(result)
        signal_str = f"Signal: {signal}" if signal else ""

        # Truncate für Anzeige (max 300 Zeichen)
        preview = result[:300] + "..." if len(result) > 300 else result

        print(f"  [{label}] {signal_str}")
        print(f"  {preview}\n")

    def _extract_signal(self, result: str) -> str:
        """Extrahiere das Signal-Level aus dem Ergebnis."""
        for signal in ["Stark", "Mittel", "Schwach"]:
            if signal in result:
                return signal
        return None
