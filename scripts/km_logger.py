"""
TechOpsKM — Activity Logger
Mencatat semua activity ke SharePoint sebagai audit log.
Setiap action (baca, tulis, proses, error) tercatat dengan detail.
"""
from dotenv import load_dotenv
load_dotenv()


import os
import json
import socket
import requests
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum

# ============================================================
# CONFIG
# ============================================================
TENANT_ID     = os.environ["SHAREPOINT_TENANT_ID"]
CLIENT_ID     = os.environ["SHAREPOINT_CLIENT_ID"]
CLIENT_SECRET = os.environ["SHAREPOINT_CLIENT_SECRET"]
SITE_ID       = "9ab69ba7-f523-4c27-ae1b-c11ddc4f74b2"  # equipment.engineering
LOG_FOLDER    = "Projects/AI Knowledge/Logs"
LOCAL_LOG     = Path("km_activity.log")

# ============================================================
# ACTION TYPES
# ============================================================
class Action(str, Enum):
    # Inbound — baca dari SharePoint
    SP_READ_START    = "SP_READ_START"
    SP_READ_SUCCESS  = "SP_READ_SUCCESS"
    SP_READ_FAIL     = "SP_READ_FAIL"
    SP_LIST_START    = "SP_LIST_START"
    SP_LIST_SUCCESS  = "SP_LIST_SUCCESS"
    SP_LIST_FAIL     = "SP_LIST_FAIL"
    # Processing
    CONVERT_START    = "CONVERT_START"
    CONVERT_SUCCESS  = "CONVERT_SUCCESS"
    CONVERT_FAIL     = "CONVERT_FAIL"
    AI_PROCESS_START = "AI_PROCESS_START"
    AI_PROCESS_OK    = "AI_PROCESS_OK"
    AI_PROCESS_FAIL  = "AI_PROCESS_FAIL"
    # Outbound — tulis ke SharePoint
    SP_WRITE_START   = "SP_WRITE_START"
    SP_WRITE_SUCCESS = "SP_WRITE_SUCCESS"
    SP_WRITE_FAIL    = "SP_WRITE_FAIL"
    # Pipeline lifecycle
    PIPELINE_START   = "PIPELINE_START"
    PIPELINE_END     = "PIPELINE_END"
    PIPELINE_ERROR   = "PIPELINE_ERROR"
    # Monitoring
    STALE_DETECTED   = "STALE_DETECTED"
    NEW_SOP_DETECTED = "NEW_SOP_DETECTED"
    REVISED_DETECTED = "REVISED_DETECTED"
    # Notification
    EMAIL_SENT       = "EMAIL_SENT"
    EMAIL_FAIL       = "EMAIL_FAIL"

# ============================================================
# LOGGER CLASS
# ============================================================
class KMLogger:
    def __init__(self, session_id=None, pipeline_name="km_pipeline"):
        self.session_id    = session_id or self._gen_session_id()
        self.pipeline_name = pipeline_name
        self.hostname      = socket.gethostname()
        self.app_id        = CLIENT_ID[:8] + "..."
        self._token        = None
        self._entries      = []

    def _gen_session_id(self):
        from datetime import datetime
        return datetime.now(timezone.utc).strftime("KM-%Y%m%d-%H%M%S")

    def _get_token(self):
        if self._token:
            return self._token
        r = requests.post(
            f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope":         "https://graph.microsoft.com/.default"
            }
        )
        r.raise_for_status()
        self._token = r.json()["access_token"]
        return self._token

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _build_entry(self, action, target=None, detail=None,
                     status="INFO", size_bytes=None, duration_ms=None,
                     error=None, metadata=None):
        entry = {
            "timestamp":     self._now(),
            "session_id":    self.session_id,
            "pipeline":      self.pipeline_name,
            "action":        action,
            "status":        status,
            "hostname":      self.hostname,
            "app_id":        self.app_id,
            "target":        target,
            "detail":        detail,
        }
        if size_bytes  is not None: entry["size_bytes"]  = size_bytes
        if duration_ms is not None: entry["duration_ms"] = duration_ms
        if error       is not None: entry["error"]       = str(error)[:300]
        if metadata    is not None: entry["metadata"]    = metadata
        return entry

    def log(self, action, target=None, detail=None, status="INFO",
            size_bytes=None, duration_ms=None, error=None, metadata=None):
        entry = self._build_entry(
            action, target, detail, status,
            size_bytes, duration_ms, error, metadata
        )
        self._entries.append(entry)

        # Tulis ke local log dulu (buffer)
        with open(LOCAL_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Print ke console
        icon = {"INFO": "→", "SUCCESS": "✓", "ERROR": "✗", "WARN": "⚠"}.get(status, "·")
        target_str = f" | {target}" if target else ""
        detail_str = f" — {detail}" if detail else ""
        print(f"[{entry['timestamp'][11:19]}] {icon} {action}{target_str}{detail_str}")

        return entry

    # ── Shorthand methods ──

    def pipeline_start(self, detail=None):
        return self.log(Action.PIPELINE_START, detail=detail, status="INFO")

    def pipeline_end(self, total, success, failed, duration_ms=None):
        return self.log(
            Action.PIPELINE_END,
            detail=f"total={total} success={success} failed={failed}",
            status="SUCCESS" if failed == 0 else "WARN",
            duration_ms=duration_ms,
            metadata={"total": total, "success": success, "failed": failed}
        )

    def sp_read_start(self, filename, path=None):
        return self.log(Action.SP_READ_START, target=filename,
                        detail=f"Reading from SharePoint: {path or ''}", status="INFO")

    def sp_read_ok(self, filename, size_bytes, duration_ms=None):
        return self.log(Action.SP_READ_SUCCESS, target=filename,
                        detail=f"Downloaded {size_bytes//1024} KB",
                        status="SUCCESS", size_bytes=size_bytes, duration_ms=duration_ms)

    def sp_read_fail(self, filename, error):
        return self.log(Action.SP_READ_FAIL, target=filename,
                        status="ERROR", error=error)

    def sp_list_start(self, folder):
        return self.log(Action.SP_LIST_START, target=folder,
                        detail="Listing SOP files", status="INFO")

    def sp_list_ok(self, folder, count, new=0, revised=0, stale=0):
        return self.log(Action.SP_LIST_SUCCESS, target=folder,
                        detail=f"Found {count} files | new={new} revised={revised} stale={stale}",
                        status="SUCCESS",
                        metadata={"count": count, "new": new, "revised": revised, "stale": stale})

    def sp_write_start(self, filename, dest_folder):
        return self.log(Action.SP_WRITE_START, target=filename,
                        detail=f"Uploading to {dest_folder}", status="INFO")

    def sp_write_ok(self, filename, size_bytes, duration_ms=None):
        return self.log(Action.SP_WRITE_SUCCESS, target=filename,
                        detail=f"Uploaded {size_bytes//1024} KB to SharePoint",
                        status="SUCCESS", size_bytes=size_bytes, duration_ms=duration_ms)

    def sp_write_fail(self, filename, error):
        return self.log(Action.SP_WRITE_FAIL, target=filename,
                        status="ERROR", error=error)

    def convert_start(self, filename):
        return self.log(Action.CONVERT_START, target=filename,
                        detail="MarkItDown PDF→MD conversion", status="INFO")

    def convert_ok(self, filename, chars, duration_ms=None):
        return self.log(Action.CONVERT_SUCCESS, target=filename,
                        detail=f"Converted to {chars} chars MD",
                        status="SUCCESS", duration_ms=duration_ms)

    def convert_fail(self, filename, error):
        return self.log(Action.CONVERT_FAIL, target=filename,
                        status="ERROR", error=error)

    def ai_start(self, filename, model="gpt-5.5"):
        return self.log(Action.AI_PROCESS_START, target=filename,
                        detail=f"Codex generating wiki | model={model}", status="INFO")

    def ai_ok(self, filename, chars, tokens=None, duration_ms=None):
        detail = f"Wiki generated {chars} chars"
        if tokens: detail += f" | tokens={tokens}"
        return self.log(Action.AI_PROCESS_OK, target=filename,
                        detail=detail, status="SUCCESS",
                        duration_ms=duration_ms,
                        metadata={"tokens": tokens} if tokens else None)

    def ai_fail(self, filename, error):
        return self.log(Action.AI_PROCESS_FAIL, target=filename,
                        status="ERROR", error=error)

    def stale_detected(self, filename, days):
        return self.log(Action.STALE_DETECTED, target=filename,
                        detail=f"Not updated in {days} days — flagged as potentially-stale",
                        status="WARN", metadata={"days_since_update": days})

    def new_sop(self, filename, path):
        return self.log(Action.NEW_SOP_DETECTED, target=filename,
                        detail=f"New SOP detected at {path}", status="INFO")

    def revised_sop(self, filename, prev_modified):
        return self.log(Action.REVISED_DETECTED, target=filename,
                        detail=f"Revision detected | previous={prev_modified[:10]}",
                        status="INFO", metadata={"previous_modified": prev_modified})

    def email_sent(self, to_email, subject):
        return self.log(Action.EMAIL_SENT, target=to_email,
                        detail=f"Subject: {subject}", status="SUCCESS")

    def email_fail(self, to_email, error):
        return self.log(Action.EMAIL_FAIL, target=to_email,
                        status="ERROR", error=error)

    # ── Upload log ke SharePoint ──

    def flush_to_sharepoint(self):
        """Upload accumulated log entries ke SharePoint sebagai NDJSON file."""
        if not self._entries:
            print("[Logger] No entries to flush")
            return

        try:
            token = self._get_token()
        except Exception as e:
            print(f"[Logger] Cannot get token for SharePoint upload: {e}")
            return

        date_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename  = f"activity-{date_str}.ndjson"
        content   = "\n".join(json.dumps(e, ensure_ascii=False) for e in self._entries)

        encoded   = LOG_FOLDER.replace(" ", "%20")
        url       = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root:/{encoded}/{filename}:/content"
        headers   = {"Authorization": f"Bearer {token}", "Content-Type": "text/plain"}

        r = requests.put(url, headers=headers, data=content.encode("utf-8"))
        if r.status_code in [200, 201]:
            print(f"[Logger] ✓ Log uploaded: {LOG_FOLDER}/{filename} ({len(self._entries)} entries)")
        else:
            print(f"[Logger] ✗ Upload failed: {r.status_code}")

        # Cleanup log lama otomatis setelah upload
        self.cleanup_old_logs(token)

    def cleanup_old_logs(self, token=None, retention_days=30):
        """
        Hapus log files di SharePoint yang sudah lebih dari retention_days hari.
        Dipanggil otomatis setiap kali flush_to_sharepoint() selesai.
        Hanya menyentuh file activity-YYYY-MM-DD.ndjson — file lain tidak disentuh.
        """
        try:
            if token is None:
                token = self._get_token()

            encoded  = LOG_FOLDER.replace(" ", "%20")
            list_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root:/{encoded}:/children"
            headers  = {"Authorization": f"Bearer {token}"}

            r = requests.get(list_url, headers=headers)
            if r.status_code != 200:
                print(f"[Logger] Cleanup skip — cannot list log folder: {r.status_code}")
                return

            items   = r.json().get("value", [])
            now     = datetime.now(timezone.utc)
            deleted = 0

            for item in items:
                name = item.get("name", "")

                # Hanya proses file activity-YYYY-MM-DD.ndjson
                if not (name.startswith("activity-") and name.endswith(".ndjson")):
                    continue

                # Parse tanggal dari nama file
                try:
                    date_str  = name.replace("activity-", "").replace(".ndjson", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    age_days  = (now - file_date).days
                except ValueError:
                    continue

                if age_days > retention_days:
                    item_id    = item["id"]
                    delete_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/items/{item_id}"
                    dr         = requests.delete(delete_url, headers=headers)

                    if dr.status_code == 204:
                        print(f"[Logger] Deleted: {name} ({age_days} days old)")
                        self.log("LOG_CLEANUP", target=name,
                                 detail=f"Auto-deleted — {age_days} days old (retention={retention_days}d)",
                                 status="INFO", metadata={"age_days": age_days})
                        deleted += 1
                    else:
                        print(f"[Logger] Failed to delete {name}: {dr.status_code}")

            if deleted > 0:
                print(f"[Logger] Cleanup done — {deleted} file(s) deleted")
            else:
                print(f"[Logger] Cleanup done — no files older than {retention_days} days")

        except Exception as e:
            print(f"[Logger] Cleanup error: {e}")

    def generate_summary_report(self):
        """Generate ringkasan session dalam format MD untuk dikirim via email."""
        success = [e for e in self._entries if e["status"] == "SUCCESS"]
        errors  = [e for e in self._entries if e["status"] == "ERROR"]
        warns   = [e for e in self._entries if e["status"] == "WARN"]

        lines = [
            f"# TechOpsKM Activity Report",
            f"**Session:** `{self.session_id}`",
            f"**Pipeline:** {self.pipeline_name}",
            f"**Generated:** {self._now()}",
            "",
            "## Summary",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✓ Success | {len(success)} |",
            f"| ⚠ Warning | {len(warns)} |",
            f"| ✗ Error | {len(errors)} |",
            f"| Total | {len(self._entries)} |",
            "",
        ]

        if errors:
            lines += ["## Errors", ""]
            for e in errors:
                lines.append(f"- `{e['action']}` on `{e.get('target','?')}`: {e.get('error','')}")
            lines.append("")

        if warns:
            lines += ["## Warnings", ""]
            for w in warns:
                lines.append(f"- `{w['action']}` on `{w.get('target','?')}`: {w.get('detail','')}")
            lines.append("")

        return "\n".join(lines)


# ============================================================
# SINGLETON — pakai ini di semua script
# ============================================================
_logger = None

def get_logger(pipeline_name="km_pipeline"):
    global _logger
    if _logger is None:
        _logger = KMLogger(pipeline_name=pipeline_name)
    return _logger

def reset_logger(pipeline_name="km_pipeline"):
    global _logger
    _logger = KMLogger(pipeline_name=pipeline_name)
    return _logger


# ============================================================
# DEMO — jalankan untuk lihat contoh log
# ============================================================
if __name__ == "__main__":
    import time

    logger = reset_logger("km_daily_demo")

    print("\n" + "="*60)
    print("TechOpsKM Logger — Demo Output")
    print("="*60 + "\n")

    # Simulasi full pipeline run
    logger.pipeline_start("Daily KM pipeline starting — PTEBIIntranet SOP scan")

    logger.sp_list_start("PTEBI SOP Library/SOP")
    time.sleep(0.1)
    logger.sp_list_ok("PTEBI SOP Library/SOP", count=47, new=2, revised=1, stale=3)

    logger.new_sop("SOP-EBI-EN-065.00 Perawatan LAF Mobile ORABS.pdf",
                   "PTEBI SOP Library/SOP/Departement Engineering")
    logger.new_sop("SOP-EBI-EN-066.00 Kalibrasi Magnehelic.pdf",
                   "PTEBI SOP Library/SOP/Departement Engineering")
    logger.revised_sop("SOP-EBI-EN-016.07 Sistem HVAC.pdf", "2025-11-03T08:22:00Z")

    logger.stale_detected("SOP-EBI-EN-001.02 Sistem Kelistrikan.pdf", days=214)
    logger.stale_detected("SOP-EBI-EN-003.03 Perawatan Gedung.pdf", days=198)
    logger.stale_detected("SOP-EBI-QA-004.04 Change Control.pdf", days=223)

    # Process SOP baru #1
    f1 = "SOP-EBI-EN-065.00 Perawatan LAF Mobile ORABS.pdf"
    logger.sp_read_start(f1, "PTEBI SOP Library/SOP/Departement Engineering")
    time.sleep(0.1)
    logger.sp_read_ok(f1, size_bytes=2_453_120, duration_ms=842)
    logger.convert_start(f1)
    time.sleep(0.1)
    logger.convert_ok(f1, chars=18_432, duration_ms=1_203)
    logger.ai_start(f1, model="gpt-5.5")
    time.sleep(0.1)
    logger.ai_ok(f1, chars=6_840, tokens=4_218, duration_ms=34_500)
    logger.sp_write_start("SOP-EBI-EN-065.00-perawatan-laf-mobile-orabs.md",
                          "Projects/AI Knowledge/Wiki")
    time.sleep(0.1)
    logger.sp_write_ok("SOP-EBI-EN-065.00-perawatan-laf-mobile-orabs.md",
                       size_bytes=6_840, duration_ms=512)

    # Process SOP baru #2 — dengan error simulasi
    f2 = "SOP-EBI-EN-066.00 Kalibrasi Magnehelic.pdf"
    logger.sp_read_start(f2, "PTEBI SOP Library/SOP/Departement Engineering")
    time.sleep(0.1)
    logger.sp_read_ok(f2, size_bytes=1_820_480, duration_ms=634)
    logger.convert_start(f2)
    time.sleep(0.1)
    logger.convert_ok(f2, chars=12_100, duration_ms=988)
    logger.ai_start(f2, model="gpt-5.5")
    time.sleep(0.1)
    logger.ai_fail(f2, error="Codex timeout after 180s — file too complex, retry needed")

    # Process revised SOP
    f3 = "SOP-EBI-EN-016.07 Sistem HVAC.pdf"
    logger.sp_read_start(f3, "PTEBI SOP Library/SOP/Departement Engineering")
    logger.sp_read_ok(f3, size_bytes=5_120_000, duration_ms=1_640)
    logger.convert_start(f3)
    logger.convert_ok(f3, chars=42_300, duration_ms=2_100)
    logger.ai_start(f3, model="gpt-5.5")
    logger.ai_ok(f3, chars=15_200, tokens=9_800, duration_ms=67_200)
    logger.sp_write_start("operasi-perawatan-hvac.md", "Projects/AI Knowledge/Wiki")
    logger.sp_write_ok("operasi-perawatan-hvac.md", size_bytes=15_200, duration_ms=430)

    # Email notification
    logger.email_sent("dito.wibowo@id.etanabiotech.com",
                      "[TechOpsKM] 2 SOP diproses — Sabtu, 17 Mei 2026")

    # Pipeline end
    logger.pipeline_end(total=3, success=2, failed=1, duration_ms=112_400)

    print("\n" + "="*60)
    print("Log entries saved to: km_activity.log")
    print("="*60)

    # Tampilkan semua entries sebagai JSON
    print("\n--- RAW LOG ENTRIES (NDJSON format) ---\n")
    for entry in logger._entries:
        print(json.dumps(entry, ensure_ascii=False))

    # Tampilkan summary report
    print("\n--- SUMMARY REPORT ---\n")
    print(logger.generate_summary_report())
