# Weather CSV Analyser

A Flask app that analyses a weather CSV and generates:
- Summary stats (min/max/averages)
- Daily breakdown
- A Matplotlib trend chart
- Demo dataset loads automatically

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
