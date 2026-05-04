import requests
import json

# === CONFIG — ganti ini ===
TENANT_ID     = "65e83e8a-2b7a-4bae-bc9c-fe2fbaedb6ab"
CLIENT_ID     = "894d1b6c-c266-4135-927c-7c337b2badba"
CLIENT_SECRET = "eYz8Q~eatnKS434dJVZYKz2u53.3R-pW-_63lanD"
SITE_NAME     = "PTEBIIntranet"  # misal: etana atau etana-techops

# === STEP 1: Ambil access token ===
print("=" * 50)
print("STEP 1: Mengambil access token...")
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
payload = {
    "grant_type":    "client_credentials",
    "client_id":     CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope":         "https://graph.microsoft.com/.default"
}

r = requests.post(token_url, data=payload)

if r.status_code == 200:
    token = r.json()["access_token"]
    print("✓ Access token berhasil didapat")
else:
    print(f"✗ Gagal dapat token: {r.status_code}")
    print(r.json())
    exit(1)

# === STEP 2: Cari SharePoint site ===
print("\nSTEP 2: Mencari SharePoint site...")
headers = {"Authorization": f"Bearer {token}"}
site_url = f"https://graph.microsoft.com/v1.0/sites?search={SITE_NAME}"

r = requests.get(site_url, headers=headers)

if r.status_code == 200:
    sites = r.json().get("value", [])
    if sites:
        print(f"✓ Site ditemukan: {len(sites)} hasil")
        for s in sites:
            print(f"  - {s['displayName']} | ID: {s['id']}")
        site_id = sites[0]["id"]
    else:
        print(f"✗ Tidak ada site dengan nama '{SITE_NAME}'")
        print("  Coba cek nama site lo di URL SharePoint")
        exit(1)
else:
    print(f"✗ Gagal akses site: {r.status_code}")
    print(r.json())
    exit(1)

# === STEP 3: List drive / document library ===
print("\nSTEP 3: Listing document library...")
drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"

r = requests.get(drive_url, headers=headers)

if r.status_code == 200:
    drives = r.json().get("value", [])
    print(f"✓ Ditemukan {len(drives)} document library:")
    for d in drives:
        print(f"  - {d['name']} | ID: {d['id']}")
else:
    print(f"✗ Gagal list drives: {r.status_code}")
    print(r.json())
    exit(1)

# === STEP 4: List file di root folder ===
print("\nSTEP 4: Listing file di root folder...")
drive_id = drives[0]["id"]
files_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children"

r = requests.get(files_url, headers=headers)

if r.status_code == 200:
    items = r.json().get("value", [])
    print(f"✓ Ditemukan {len(items)} item di root:")
    for item in items:
        tipe = "📁" if "folder" in item else "📄"
        print(f"  {tipe} {item['name']}")
else:
    print(f"✗ Gagal list files: {r.status_code}")
    print(r.json())
    exit(1)

print("\n" + "=" * 50)
print("✓ SEMUA STEP BERHASIL — SharePoint bisa dibaca!")
print("=" * 50)