import os
import json
from openai import OpenAI


class AnalyseAgent:
    """Generischer Agent-Runner für die Multi-Agent-Pipeline."""

    def __init__(self, api_key: str):
        """Initialisiere den OpenAI-Client."""
        if not api_key:
            raise ValueError("API-Schlüssel erforderlich!")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def run(self, step_name: str, system_prompt: str, user_prompt: str) -> dict:
        """
        Führe einen Analyse-Schritt durch.

        Args:
            step_name: Name des Schritts (für Logging/Debug)
            system_prompt: System-Prompt für den Agent
            user_prompt: User-Prompt mit spezifischen Anweisungen

        Returns:
            Dict mit keys: analysis, sources, assumptions, counter_arguments, signal
        """
        print(f"  → Analysiere ({step_name})...", end="", flush=True)

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            response_text = message.choices[0].message.content

            # Parse structured response (not JSON as API doesn't follow instructions)
            try:
                parsed = self._parse_response(response_text)
                print(" ✓")
                return parsed
            except Exception as e:
                print(f" ✗ Parse Error: {str(e)}")
                raise ValueError(f"Failed to parse response: {str(e)}\nResponse: {response_text[:500]}...")

        except Exception as e:
            print(f" ✗ Fehler: {str(e)}")
            raise

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the response, handling both plain text and JSON formats.
        """
        # First try to extract JSON from markdown or plain JSON
        json_text = self._extract_json(response_text)
        if json_text:
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass  # Fall back to text parsing

        # Fall back to text parsing
        result = {
            "analysis": "",
            "signal": "Unbekannt",
            "sources": [],
            "assumptions": [],
            "counter_arguments": []
        }

        lines = response_text.strip().split('\n')
        current_section = "analysis"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for signal
            if line.lower().startswith("signal:"):
                signal_part = line.split(":", 1)[1].strip().lower()
                if "stark" in signal_part:
                    result["signal"] = "Stark"
                elif "mittel" in signal_part or "moderat" in signal_part:
                    result["signal"] = "Mittel"
                elif "schwach" in signal_part:
                    result["signal"] = "Schwach"
                continue

            # Check for sections
            lower_line = line.lower()
            if any(word in lower_line for word in ["quellen", "sources", "daten", "evidenz"]):
                current_section = "sources"
                continue
            elif any(word in lower_line for word in ["annahmen", "assumptions", "voraussetzungen"]):
                current_section = "assumptions"
                continue
            elif any(word in lower_line for word in ["gegenperspektive", "gegenargument", "skeptiker", "kritik", "counter"]):
                current_section = "counter_arguments"
                continue

            # Add content to current section
            if current_section == "analysis":
                if not result["analysis"]:
                    result["analysis"] = line
                else:
                    result["analysis"] += " " + line
            elif current_section in ["sources", "assumptions", "counter_arguments"]:
                # Clean up bullet points and add to list
                clean_line = line.lstrip("•-* ").strip()
                if clean_line and len(clean_line) > 3:  # Avoid too short items
                    result[current_section].append(clean_line)

        # If no signal was found, try to infer from content or set default
        if result["signal"] == "Unbekannt":
            analysis_lower = result["analysis"].lower()
            if any(word in analysis_lower for word in ["stark", "sehr", "deutlich", "klar"]):
                result["signal"] = "Stark"
            elif any(word in analysis_lower for word in ["mittel", "moderat", "teilweise"]):
                result["signal"] = "Mittel"
            elif any(word in analysis_lower for word in ["schwach", "wenig", "kaum"]):
                result["signal"] = "Schwach"
            else:
                result["signal"] = "Mittel"  # Default

        # Ensure we have at least basic analysis
        if not result["analysis"]:
            result["analysis"] = response_text[:500] + "..." if len(response_text) > 500 else response_text

        return result

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text, handling markdown code blocks.
        """
        import re

        # Try to find JSON in markdown code blocks
        json_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_block:
            return json_block.group(1)

        # Try to find plain JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group()

        return None
        """
        Parse the structured text response into a dictionary.

        Expected format:
        - Analysis text
        - Signal: Stark/Mittel/Schwach
        - Sources/Assumptions
        - Counter arguments
        """
        result = {
            "analysis": "",
            "signal": "Unbekannt",
            "sources": [],
            "assumptions": [],
            "counter_arguments": []
        }

        lines = response_text.strip().split('\n')
        current_section = "analysis"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for signal
            if line.lower().startswith("signal:"):
                signal_part = line.split(":", 1)[1].strip()
                if "stark" in signal_part.lower():
                    result["signal"] = "Stark"
                elif "mittel" in signal_part.lower():
                    result["signal"] = "Mittel"
                elif "schwach" in signal_part.lower():
                    result["signal"] = "Schwach"
                continue

            # Check for sections
            if "quellen" in line.lower() or "sources" in line.lower():
                current_section = "sources"
                continue
            elif "annahmen" in line.lower() or "assumptions" in line.lower():
                current_section = "assumptions"
                continue
            elif "gegenperspektive" in line.lower() or "gegenstimme" in line.lower() or "counter" in line.lower():
                current_section = "counter_arguments"
                continue

            # Add content to current section
            if current_section == "analysis":
                if not result["analysis"]:
                    result["analysis"] = line
                else:
                    result["analysis"] += " " + line
            elif current_section == "sources":
                if line.startswith("- ") or line.startswith("• "):
                    result["sources"].append(line[2:].strip())
                elif line:
                    result["sources"].append(line)
            elif current_section == "assumptions":
                if line.startswith("- ") or line.startswith("• "):
                    result["assumptions"].append(line[2:].strip())
                elif line:
                    result["assumptions"].append(line)
            elif current_section == "counter_arguments":
                if line.startswith("- ") or line.startswith("• "):
                    result["counter_arguments"].append(line[2:].strip())
                elif line:
                    result["counter_arguments"].append(line)

        # If no signal was found, try to infer from content
        if result["signal"] == "Unbekannt":
            analysis_lower = result["analysis"].lower()
            if "stark" in analysis_lower:
                result["signal"] = "Stark"
            elif "mittel" in analysis_lower or "moderat" in analysis_lower:
                result["signal"] = "Mittel"
            elif "schwach" in analysis_lower:
                result["signal"] = "Schwach"

        return result
