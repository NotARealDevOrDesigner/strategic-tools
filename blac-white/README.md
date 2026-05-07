# BLAC & White

Strategic analysis tool based on Michael Skok's BLAC & White framework (Harvard Innovation Lab).

Enter a problem, solution, and target segments — the tool evaluates whether the opportunity is worth pursuing and returns a Go/No-Go decision with a strategic roadmap.

**Three dimensions scored 1–10:**
- **Visibility** — is the problem obvious (Blatant) or hidden (Latent)?
- **Criticality** — is solving it urgent (Critical) or optional (Aspirational)?
- **White Space** — how open is the market for a new solution?

**Analysis depths:** Memory · Quick · Standard · Deep

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn app:app --reload
```

Open `http://localhost:8000`.
