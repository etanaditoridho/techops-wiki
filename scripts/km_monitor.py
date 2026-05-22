"""
TechOpsKM — Knowledge Monitor
Deteksi perubahan SOP di SharePoint PTEBIIntranet:
- File baru (belum ada di state)
- File direvisi (lastModifiedDateTime berubah)
- File stale (tidak diupdate > threshold hari)
"""
from dotenv import load_dotenv
load_dotenv()


import os
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from km_logger import get_logger

# ============================================================
# CONFIG
# ============================================================
TENANT_ID      = os.environ["SHAREPOINT_TENANT_ID"]
CLIENT_ID      = os.environ["SHAREPOINT_CLIENT_ID"]
CLIENT_SECRET  = os.environ["SHAREPOINT_CLIENT_SECRET"]
SITE_ID        = "78d158e2-b13f-4d92-9235-12f054517ee9"  # PTEBIIntranet
DRIVE_ID       = "b!4ljReD-xkk2SNRLwVFF-6RYXGWai4FBOn2JCqjHwwogAFMwOg-A5Tb5abJ03zQVx"  # Document Library
SOP_FOLDER     = "SOP"  # relatif dari root drive Document Library
STALE_DAYS     = int(os.environ.get("STALE_THRESHOLD_DAYS", "180"))
STATE_FILE     = Path("km_state.json")

# ============================================================
# AUTH
# ============================================================
def get_token():
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
    return r.json()["access_token"]

# ============================================================
# SHAREPOINT — LIST FILES
# ============================================================
def list_sop_files(token, folder_path=SOP_FOLDER):
    encoded = folder_path.replace(" ", "%20").replace("&", "%26")
    url     = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/root:/{encoded}:/children"
    headers = {"Authorization": f"Bearer {token}"}
    all_files = []
    while url:
        r    = requests.get(url, headers=headers)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data  = r.json()
        items = data.get("value", [])
        for item in items:
            if "folder" in item:
                sub_path = f"{folder_path}/{item['name']}"
                all_files.extend(list_sop_files(token, sub_path))
            elif item["name"].lower().endswith(".pdf"):
                all_files.append({
                    "id":           item["id"],
                    "name":         item["name"],
                    "path":         folder_path,
                    "full_path":    f"{folder_path}/{item['name']}",
                    "department":   folder_path.split("/")[-1] if "/" in folder_path else "",
                    "size":         item.get("size", 0),
                    "modified":     item["lastModifiedDateTime"],
                    "download_url": item.get("@microsoft.graph.downloadUrl", ""),
                    "web_url":      item.get("webUrl", ""),
                })
        url = data.get("@odata.nextLink")
    return all_files

# ============================================================
# STATE MANAGEMENT
# ============================================================
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ============================================================
# CHANGE DETECTION
# ============================================================
def detect_changes(current_files, previous_state):
    now              = datetime.now(timezone.utc)
    stale_threshold  = now - timedelta(days=STALE_DAYS)
    new_files        = []
    revised_files    = []
    stale_files      = []
    unchanged        = []

    for f in current_files:
        fid      = f["id"]
        modified = datetime.fromisoformat(f["modified"].replace("Z", "+00:00"))
        prev     = previous_state.get(fid)

        if prev is None:
            new_files.append(f)
        elif prev["modified"] != f["modified"]:
            f["previous_modified"] = prev["modified"]
            revised_files.append(f)
        else:
            if modified < stale_threshold:
                f["days_since_update"] = (now - modified).days
                stale_files.append(f)
            else:
                unchanged.append(f)

    return {
        "new":       new_files,
        "revised":   revised_files,
        "stale":     stale_files,
        "unchanged": unchanged,
        "total":     len(current_files),
        "checked_at": now.isoformat(),
    }

# ============================================================
# UPDATE STATE
# ============================================================
def update_state(current_files, previous_state):
    new_state = dict(previous_state)
    for f in current_files:
        new_state[f["id"]] = {
            "name":     f["name"],
            "path":     f["path"],
            "modified": f["modified"],
            "size":     f["size"],
        }
    return new_state

# ============================================================
# MAIN
# ============================================================
def run():
    logger = get_logger("km_monitor")
    logger.pipeline_start(f"SharePoint SOP scan — stale threshold {STALE_DAYS} days")

    token = get_token()
    logger.sp_list_start(SOP_FOLDER)

    current_files  = list_sop_files(token)
    previous_state = load_state()
    changes        = detect_changes(current_files, previous_state)

    # Log setiap perubahan yang terdeteksi
    for f in changes["new"]:
        logger.new_sop(f["name"], f["path"])
    for f in changes["revised"]:
        logger.revised_sop(f["name"], f.get("previous_modified", ""))
    for f in changes["stale"]:
        logger.stale_detected(f["name"], f.get("days_since_update", 0))

    logger.sp_list_ok(
        SOP_FOLDER,
        count=changes["total"],
        new=len(changes["new"]),
        revised=len(changes["revised"]),
        stale=len(changes["stale"])
    )

    if changes["new"] or changes["revised"]:
        new_state = update_state(current_files, previous_state)
        save_state(new_state)

    Path("km_changes.json").write_text(json.dumps(changes, indent=2))
    logger.log("STATE_SAVED", target="km_changes.json",
               detail=f"Changes saved — {len(changes['new'])} new, {len(changes['revised'])} revised",
               status="SUCCESS")

    logger.flush_to_sharepoint()
    return changes

if __name__ == "__main__":
    run()
