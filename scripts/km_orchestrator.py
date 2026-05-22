"""
TechOpsKM — Orchestrator
Jalankan full pipeline secara berurutan dengan error handling dan logging.
Schedule via Windows Task Scheduler.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================
BASE_DIR    = Path(__file__).parent.parent  # techops-wiki/
SCRIPTS_DIR = BASE_DIR / "scripts"
VAULT_DIR   = Path(os.environ.get("OBSIDIAN_VAULT", r"C:\Dito\Digitalization\TechOpsKM\obsidian-vault"))
LOG_DIR     = BASE_DIR / "logs"
RCLONE      = r"C:\rclone\rclone.exe"
SFTP_REMOTE = "sftp:/sop/aikms"
PYTHON      = sys.executable

LOG_DIR.mkdir(exist_ok=True)

# Setup logging
log_file = LOG_DIR / f"orchestrator-{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("orchestrator")

# ============================================================
# HELPERS
# ============================================================
def run_step(name, script_path, cwd=None):
    """Jalankan satu step pipeline, return True kalau sukses."""
    log.info(f"▶ START: {name}")
    start = datetime.now()
    try:
        result = subprocess.run(
            [PYTHON, str(script_path)],
            cwd=str(cwd or BASE_DIR),
            capture_output=False,
            timeout=3600,  # max 1 jam per step
        )
        elapsed = (datetime.now() - start).seconds
        if result.returncode == 0:
            log.info(f"✓ OK: {name} ({elapsed}s)")
            return True
        else:
            log.error(f"✗ FAIL: {name} — returncode {result.returncode} ({elapsed}s)")
            return False
    except subprocess.TimeoutExpired:
        log.error(f"✗ TIMEOUT: {name} — exceeded 1 hour")
        return False
    except Exception as e:
        log.error(f"✗ ERROR: {name} — {e}")
        return False

def run_rclone(src, dst, label):
    """Jalankan rclone sync."""
    log.info(f"▶ SYNC: {label}")
    start = datetime.now()
    try:
        result = subprocess.run(
            [RCLONE, "sync", src, dst, "--progress"],
            capture_output=False,
            timeout=600,
        )
        elapsed = (datetime.now() - start).seconds
        if result.returncode == 0:
            log.info(f"✓ SYNC OK: {label} ({elapsed}s)")
            return True
        else:
            log.error(f"✗ SYNC FAIL: {label} — returncode {result.returncode}")
            return False
    except Exception as e:
        log.error(f"✗ SYNC ERROR: {label} — {e}")
        return False

def check_changes():
    """Cek apakah ada perubahan di km_changes.json."""
    changes_file = BASE_DIR / "km_changes.json"
    if not changes_file.exists():
        return True  # Tidak ada state → anggap ada perubahan
    try:
        data = json.loads(changes_file.read_text(encoding="utf-8"))
        new_count      = len(data.get("new", []))
        revised_count  = len(data.get("revised", []))
        log.info(f"[Changes] new={new_count}, revised={revised_count}")
        return (new_count + revised_count) > 0
    except Exception:
        return True

# ============================================================
# MAIN PIPELINE
# ============================================================
def run(force=False):
    start_time = datetime.now()
    log.info("=" * 60)
    log.info(f"TechOpsKM Pipeline START — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    results = {}

    # STEP 1 — Monitor SharePoint
    ok = run_step("Monitor SharePoint", SCRIPTS_DIR / "km_monitor.py")
    results["monitor"] = ok
    if not ok:
        log.error("Monitor gagal — pipeline dihentikan")
        _save_summary(results, start_time)
        return False

    # Cek apakah ada perubahan — skip processor kalau tidak ada
    has_changes = check_changes()
    if not has_changes and not force:
        log.info("Tidak ada perubahan di SharePoint — skip processor, relate, wiki")
        # Tetap sync supaya vault selalu fresh
        run_rclone(SFTP_REMOTE, "b2-techops:techopskm-docs", "SFTP → Backblaze B2")
        run_rclone("b2-techops:techopskm-docs", str(VAULT_DIR), "B2 → Local vault")
        _save_summary(results, start_time)
        return True

    # STEP 2 — Process SOP (download, convert, AI, upload SFTP)
    ok = run_step("Process SOP", SCRIPTS_DIR / "km_processor.py")
    results["processor"] = ok
    if not ok:
        log.warning("Processor gagal — lanjut ke relate dengan data existing")

    # STEP 3 — Auto-relate wikilinks
    ok = run_step("Auto-relate", SCRIPTS_DIR / "km_relate.py")
    results["relate"] = ok

    # STEP 4 — Generate wiki pages
    ok = run_step("Wiki generator", SCRIPTS_DIR / "km_wiki.py")
    results["wiki"] = ok

    # STEP 5 — Build search index
    ok = run_step("Build search index", SCRIPTS_DIR / "km_build_index.py")
    results["build_index"] = ok

    # STEP 6 — Sync SFTP → B2 (mirror untuk MCP + backup cloud)
    ok = run_rclone(SFTP_REMOTE, "b2-techops:techopskm-docs", "SFTP → Backblaze B2")
    results["sync_b2"] = ok

    # STEP 7 — Clone B2 → Local vault (Obsidian baca dari B2)
    ok = run_rclone("b2-techops:techopskm-docs", str(VAULT_DIR), "B2 → Local vault")
    results["sync_local"] = ok

    # Summary
    _save_summary(results, start_time)

    elapsed = (datetime.now() - start_time).seconds
    success  = sum(1 for v in results.values() if v)
    total    = len(results)
    log.info("=" * 60)
    log.info(f"Pipeline SELESAI — {success}/{total} steps OK — {elapsed}s")
    log.info("=" * 60)
    return success == total

def _save_summary(results, start_time):
    summary = {
        "timestamp": start_time.isoformat(),
        "duration_s": (datetime.now() - start_time).seconds,
        "results": {k: "OK" if v else "FAIL" for k, v in results.items()},
    }
    summary_path = BASE_DIR / "km_pipeline_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info(f"Summary saved → {summary_path}")

if __name__ == "__main__":
    force = "--force" in sys.argv
    success = run(force=force)
    sys.exit(0 if success else 1)
