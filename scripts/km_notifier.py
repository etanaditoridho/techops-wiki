"""
TechOpsKM — Knowledge Notifier
Kirim email summary via Gmail SMTP.
Tidak butuh permission tambahan dari IT.
"""
from dotenv import load_dotenv
load_dotenv()


import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from km_logger import get_logger

# ============================================================
# CONFIG
# ============================================================
GMAIL_USER     = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
KM_LEAD_EMAIL  = os.environ.get("KM_LEAD_EMAIL", GMAIL_USER)
CHANGES_FILE   = Path("km_changes.json")
PROCESSED_LOG  = Path("km_processed.json")

# ============================================================
# SEND EMAIL
# ============================================================
def send_email(to_email, subject, html_body):
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

# ============================================================
# BUILD DAILY EMAIL
# ============================================================
def build_daily_email(changes, processed):
    now       = datetime.now().strftime("%A, %d %B %Y")
    new_files = changes.get("new", [])
    revised   = changes.get("revised", [])
    stale     = changes.get("stale", [])
    results   = processed.get("results", [])
    summary   = processed.get("summary", {})

    if not new_files and not revised and not stale:
        return None, None

    count   = len(new_files) + len(revised)
    subject = f"[TechOpsKM] {count} SOP diproses — {now}" if count else f"[TechOpsKM] Daily Update — {now}"

    def rows(files, label, color):
        out = ""
        for f in files:
            extra = f" ({f.get('days_since_update','?')} hari)" if label == "Stale" else \
                    f" (prev: {f.get('previous_modified','')[:10]})" if label == "Revisi" else ""
            dept = f.get("path", "").split("/")[-1]
            out += f"""<tr>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;">
                <span style="background:{color};color:white;font-size:10px;padding:2px 6px;border-radius:4px;margin-right:6px">{label}</span>
                {f['name']}{extra}
              </td>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;color:#666;font-size:12px">{dept}</td>
            </tr>"""
        return out

    error_rows = "".join(
        f"<tr><td colspan='2' style='padding:8px 12px;color:#c0392b;font-size:12px'>✗ {r['name']}: {r.get('error','')[:80]}</td></tr>"
        for r in results if r["status"] == "error"
    )

    html = f"""<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#333">
<div style="background:#0EA5E9;padding:20px 24px;border-radius:8px 8px 0 0">
  <h2 style="margin:0;color:white;font-size:18px">TechOpsKM — Daily Knowledge Update</h2>
  <p style="margin:4px 0 0;color:#BAE6FD;font-size:13px">{now}</p>
</div>
<div style="background:#f8f9fa;padding:16px 24px;border:1px solid #e9ecef;display:flex;gap:32px">
  <div style="text-align:center"><div style="font-size:28px;font-weight:bold;color:#0EA5E9">{len(new_files)}</div><div style="font-size:12px;color:#666">SOP Baru</div></div>
  <div style="text-align:center"><div style="font-size:28px;font-weight:bold;color:#38BDF8">{len(revised)}</div><div style="font-size:12px;color:#666">Direvisi</div></div>
  <div style="text-align:center"><div style="font-size:28px;font-weight:bold;color:#F59E0B">{len(stale)}</div><div style="font-size:12px;color:#666">Stale</div></div>
  <div style="text-align:center"><div style="font-size:28px;font-weight:bold;color:{'#10B981' if summary.get('error',0)==0 else '#EF4444'}">{summary.get('success',0)}/{summary.get('total',0)}</div><div style="font-size:12px;color:#666">Berhasil</div></div>
</div>
<div style="padding:20px 24px;border:1px solid #e9ecef;border-top:none">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="background:#f8f9fa">
      <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666">File</th>
      <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666">Departemen</th>
    </tr></thead>
    <tbody>
      {rows(new_files, "Baru", "#10B981")}
      {rows(revised, "Revisi", "#0EA5E9")}
      {rows(stale, "Stale", "#F59E0B")}
      {error_rows}
    </tbody>
  </table>
  {'<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:6px;padding:10px;margin-top:8px;font-size:12px;color:#DC2626"><b>⚠ ' + str(summary.get("error",0)) + " file gagal diproses</b> — cek GitHub Actions log untuk detail.</div>" if summary.get("error",0) > 0 else ""}
</div>
<div style="padding:12px 24px;background:#f8f9fa;border:1px solid #e9ecef;border-top:none;border-radius:0 0 8px 8px">
  <p style="margin:0;font-size:11px;color:#999">TechOpsKM Automated System — PT Etana Biotechnologies Indonesia<br>
  Log tersimpan di SharePoint: equipment.engineering/Projects/AI Knowledge/Logs</p>
</div></body></html>"""

    return subject, html

# ============================================================
# BUILD WEEKLY EMAIL
# ============================================================
def build_weekly_email():
    week = datetime.now().strftime("Week %W, %Y")
    now  = datetime.now().strftime("%d %B %Y")

    total_new = total_revised = total_stale = total_err = 0
    daily_rows = ""

    for log_file in sorted(Path(".").glob("km_processed_*.json"), reverse=True)[:7]:
        try:
            log  = json.loads(log_file.read_text())
            date = log_file.stem.replace("km_processed_", "")
            res  = log.get("results", [])
            n    = len([r for r in res if r["status"] == "new"])
            rv   = len([r for r in res if r["status"] == "revised"])
            st   = len([r for r in res if r["status"] == "stale_flagged"])
            er   = log.get("summary", {}).get("error", 0)
            total_new += n; total_revised += rv; total_stale += st; total_err += er
            daily_rows += f"""<tr>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;font-size:13px">{date}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;color:#10B981;font-weight:bold">{n}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;color:#0EA5E9;font-weight:bold">{rv}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;color:#F59E0B;font-weight:bold">{st}</td>
            </tr>"""
        except Exception:
            continue

    subject = f"[TechOpsKM] Weekly Digest — {week}"
    html = f"""<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#333">
<div style="background:#0EA5E9;padding:20px 24px;border-radius:8px 8px 0 0">
  <h2 style="margin:0;color:white;font-size:18px">TechOpsKM — Weekly Digest</h2>
  <p style="margin:4px 0 0;color:#BAE6FD;font-size:13px">{week} · Dikirim {now}</p>
</div>
<div style="background:#f8f9fa;padding:16px 24px;border:1px solid #e9ecef;display:flex;gap:32px">
  <div style="text-align:center"><div style="font-size:36px;font-weight:bold;color:#10B981">{total_new}</div><div style="font-size:12px;color:#666">SOP Baru</div></div>
  <div style="text-align:center"><div style="font-size:36px;font-weight:bold;color:#0EA5E9">{total_revised}</div><div style="font-size:12px;color:#666">Direvisi</div></div>
  <div style="text-align:center"><div style="font-size:36px;font-weight:bold;color:#F59E0B">{total_stale}</div><div style="font-size:12px;color:#666">Stale</div></div>
</div>
<div style="padding:20px 24px;border:1px solid #e9ecef;border-top:none">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="background:#f8f9fa">
      <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666">Hari</th>
      <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666">Baru</th>
      <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666">Revisi</th>
      <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666">Stale</th>
    </tr></thead>
    <tbody>{daily_rows or '<tr><td colspan="4" style="padding:12px;text-align:center;color:#999">Tidak ada data minggu ini</td></tr>'}</tbody>
  </table>
</div>
<div style="padding:12px 24px;background:#f8f9fa;border:1px solid #e9ecef;border-top:none;border-radius:0 0 8px 8px">
  <p style="margin:0;font-size:11px;color:#999">TechOpsKM Automated System — PT Etana Biotechnologies Indonesia</p>
</div></body></html>"""

    return subject, html

# ============================================================
# MAIN
# ============================================================
def run_daily():
    logger = get_logger("km_notifier_daily")
    if not CHANGES_FILE.exists() or not PROCESSED_LOG.exists():
        return

    changes   = json.loads(CHANGES_FILE.read_text())
    processed = json.loads(PROCESSED_LOG.read_text())
    subject, html = build_daily_email(changes, processed)

    if subject is None:
        logger.log("EMAIL_SKIP", detail="No changes — email not sent", status="INFO")
        logger.flush_to_sharepoint()
        return

    try:
        send_email(KM_LEAD_EMAIL, subject, html)
        logger.email_sent(KM_LEAD_EMAIL, subject)
    except Exception as e:
        logger.email_fail(KM_LEAD_EMAIL, e)

    logger.flush_to_sharepoint()

def run_weekly():
    logger          = get_logger("km_notifier_weekly")
    subject, html   = build_weekly_email()
    try:
        send_email(KM_LEAD_EMAIL, subject, html)
        logger.email_sent(KM_LEAD_EMAIL, subject)
    except Exception as e:
        logger.email_fail(KM_LEAD_EMAIL, e)
    logger.flush_to_sharepoint()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "weekly":
        run_weekly()
    else:
        run_daily()
