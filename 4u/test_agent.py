#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from agents.analyse_agent import AnalyseAgent
from prompts.four_u_prompts import SYSTEM_PROMPT, STEP_PROMPTS

load_dotenv()

agent = AnalyseAgent()
problem = "Manuelle Rechnungsstellung ist zeitaufwändig"
user_prompt = STEP_PROMPTS["unworkable"].format(problem=problem)

print("=" * 60)
print("Testing UNWORKABLE Analysis")
print("=" * 60 + "\n")

try:
    result = agent.run("UNWORKABLE", SYSTEM_PROMPT, user_prompt)
    print("\nPARSED RESULT:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
