import json, hashlib
from pathlib import Path

RAW_DIR = Path(r"C:\Dito\Digitalization\TechOpsKM\techops-wiki\raw")
STATE_FILE = Path(r"C:\Dito\Digitalization\TechOpsKM\techops-wiki\.raw-ingest-state.json")

state = {}
for pdf in RAW_DIR.rglob("*.pdf"):
    rel = str(pdf.relative_to(RAW_DIR)).replace("\\", "/")
    h = hashlib.md5(pdf.read_bytes()).hexdigest()
    state[rel] = {"hash": h, "wiki": ""}

STATE_FILE.write_text(json.dumps(state, indent=2))
print(f"Generated state for {len(state)} PDFs")
for k in state:
    print(f"  {k}")