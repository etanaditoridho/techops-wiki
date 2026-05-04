"""
sharepoint_client.py
Koneksi ke Microsoft Graph API untuk scan dan baca file dari SharePoint.
Tidak menyimpan file di local — hanya baca ke memory.

Credentials dibaca dari environment variables (.env file).
"""

import os
import requests
from typing import Optional

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token() -> str:
    """
    Ambil access token dari Azure AD menggunakan client credentials flow.
    Token ini digunakan untuk semua request ke Microsoft Graph API.
    """
    tenant_id     = os.environ["AZURE_TENANT_ID"]
    client_id     = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "scope":         "https://graph.microsoft.com/.default",
    }

    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── SharePoint helpers ────────────────────────────────────────────────────────

def get_site_id(token: str, site_url: str) -> str:
    """
    Ambil SharePoint site ID dari URL site.
    Contoh site_url: https://etanabiotechid.sharepoint.com/sites/PTEBIIntranet
    """
    # Parse hostname dan site path dari URL
    # https://etanabiotechid.sharepoint.com/sites/PTEBIIntranet
    # → hostname: etanabiotechid.sharepoint.com
    # → site_path: /sites/PTEBIIntranet
    from urllib.parse import urlparse
    parsed   = urlparse(site_url)
    hostname = parsed.netloc
    sitepath = parsed.path  # /sites/PTEBIIntranet

    url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{sitepath}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["id"]


def get_drive_id(token: str, site_id: str) -> str:
    """
    Ambil ID default document library (drive) dari site.
    """
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["id"]


def list_files_in_folder(token: str, site_id: str, drive_id: str, folder_path: str) -> list[dict]:
    """
    List semua file di folder SharePoint secara rekursif.
    Returns list of {name, id, size, lastModifiedDateTime, download_url}

    folder_path contoh: "PTEBI SOP Library/SOP/Departement Engineering"
    """
    # Encode folder path untuk URL
    encoded_path = folder_path.replace(" ", "%20")
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
    headers = {"Authorization": f"Bearer {token}"}

    files = []
    while url:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("value", []):
            if "file" in item:  # ini file, bukan folder
                ext = item["name"].lower().split(".")[-1]
                if ext in {"pdf", "docx", "pptx", "xlsx", "doc", "xls"}:
                    files.append({
                        "name":             item["name"],
                        "id":               item["id"],
                        "size":             item.get("size", 0),
                        "last_modified":    item.get("lastModifiedDateTime", ""),
                        "download_url":     item.get("@microsoft.graph.downloadUrl", ""),
                    })
            elif "folder" in item:  # rekursif ke subfolder
                subfolder_path = f"{folder_path}/{item['name']}"
                sub_files = list_files_in_folder(token, site_id, drive_id, subfolder_path)
                files.extend(sub_files)

        # Handle pagination
        url = data.get("@odata.nextLink")

    return files


def download_file_to_memory(token: str, download_url: str) -> bytes:
    """
    Download file dari SharePoint ke memory (bytes).
    File TIDAK disimpan ke disk — langsung diproses di memory.
    """
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(download_url, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.content


# ── Main scanner ──────────────────────────────────────────────────────────────

def scan_sharepoint() -> tuple[str, str, str, list[dict]]:
    """
    Scan SharePoint folder dan return list file yang tersedia.
    Returns: (token, site_id, drive_id, list_of_files)
    """
    site_url      = os.environ["SHAREPOINT_SITE_URL"]
    folder_path   = os.environ["SHAREPOINT_FOLDER"]

    print(f"[sharepoint] Authenticating to Azure AD...")
    token = get_access_token()
    print(f"[sharepoint] ✓ Token obtained")

    print(f"[sharepoint] Getting site ID for: {site_url}")
    site_id = get_site_id(token, site_url)
    print(f"[sharepoint] ✓ Site ID: {site_id}")

    print(f"[sharepoint] Getting drive ID...")
    drive_id = get_drive_id(token, site_id)
    print(f"[sharepoint] ✓ Drive ID: {drive_id}")

    print(f"[sharepoint] Scanning folder: {folder_path}")
    files = list_files_in_folder(token, site_id, drive_id, folder_path)
    print(f"[sharepoint] ✓ Found {len(files)} files")

    return token, site_id, drive_id, files


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    token, site_id, drive_id, files = scan_sharepoint()
    print(f"\nFiles found ({len(files)}):")
    for f in files:
        print(f"  - {f['name']} ({f['size']:,} bytes) | modified: {f['last_modified'][:10]}")
