import sys
import os
from dotenv import load_dotenv
from methods.four_u import FourUMethod


def main():
    """
    Einstiegspunkt für die 4U-Analyse-Pipeline.

    Akzeptiert:
    - CLI-Argument: python main.py "mein problem" "api_key"
    - Interaktive Eingabe: python main.py
    """
    # Lade .env-Datei (aber verwende nicht den Schlüssel daraus)
    load_dotenv()

    # Hole Problem und API-Schlüssel aus CLI-Argumenten oder interaktiver Eingabe
    if len(sys.argv) > 2:
        problem = sys.argv[1]
        api_key = sys.argv[2]
    elif len(sys.argv) > 1:
        problem = sys.argv[1]
        api_key = input("Gib deinen OpenAI API-Schlüssel ein:\n> ").strip()
    else:
        print("4U-Analyse-Pipeline")
        print("-" * 50)
        problem = input("Gib das zu analysierende Problem ein:\n> ").strip()
        api_key = input("Gib deinen OpenAI API-Schlüssel ein:\n> ").strip()

    if not problem:
        print("Fehler: Problem darf nicht leer sein!")
        sys.exit(1)

    if not api_key:
        print("Fehler: API-Schlüssel erforderlich!")
        sys.exit(1)

    # Führe Analyse durch
    try:
        method = FourUMethod(api_key)
        results = method.run(problem)

        # Ausgabe speichern optional
        print("\n✓ Analyse abgeschlossen!")
        print(f"Ergebnisse gespeichert in results dict mit keys:")
        print(f"  - unworkable, unavoidable, urgent, underserved, synthese")

    except ValueError as e:
        print(f"Fehler: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Fehler während Analyse: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
