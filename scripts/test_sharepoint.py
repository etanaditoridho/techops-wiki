import requests

# === CONFIG ===
TENANT_ID     = "65e83e8a-2b7a-4bae-bc9c-fe2fbaedb6ab"
CLIENT_ID     = "894d1b6c-c266-4135-927c-7c337b2badba"
CLIENT_SECRET = "eYz8Q~eatnKS434dJVZYKz2u53.3R-pW-_63lanD"

# Site yang mau di-grant — isi setelah dapat site ID dari Step 3a
SITES_TO_GRANT = [
    {"name": "PTEBIIntranet", "site_id": "78d158e2-b13f-4d92-9235-12f054517ee9"},  # isi setelah dicari
]

# === STEP 3a: Cari site ID dulu pakai akun lo (delegated) ===
# Jalankan ini dulu untuk dapat site ID ketiga site
def find_site_id(token, site_name):
    url = f"https://graph.microsoft.com/v1.0/sites?search={site_name}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    sites = r.json().get("value", [])
    print(f"\nHasil pencarian '{site_name}':")
    for s in sites:
        print(f"  - {s['displayName']} | ID: {s['id']}")
    return sites

# === STEP 3b: Grant akses app ke site ===
def grant_app_to_site(token, site_id, site_name):
    """
    Grant permission 'read' untuk app lo ke site spesifik.
    Endpoint ini butuh token dari akun yang jadi Site Owner.
    """
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/permissions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "roles": ["read"],
        "grantedToIdentities": [
            {
                "application": {
                    "id":          CLIENT_ID,
                    "displayName": "etana-km-app"
                }
            }
        ]
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        print(f"  ✓ Akses granted ke site: {site_name}")
    else:
        print(f"  ✗ Gagal grant ke {site_name}: {r.status_code}")
        print(f"    {r.json()}")

# === GET TOKEN (pakai client credentials setelah Sites.Selected di-consent) ===
def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    r = requests.post(url, data={
        "grant_type":    "client_credentials",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def main():
    print("Mengambil token...")
    token = get_token()
    print("✓ Token didapat")

    # Step 3a: Cari site ID dulu
    print("\n=== CARI SITE ID ===")
    print("Cari site Engineering:")
    find_site_id(token, "Engineering")
    print("\nCari site QA:")
    find_site_id(token, "QA")
    print("\nCari site QS:")
    find_site_id(token, "QS")

    print("\n=== ISI site_id di SITES_TO_GRANT dulu, lalu uncomment bagian grant ===")

    # Step 3b: Setelah site ID diisi, uncomment bagian ini
    # print("\n=== GRANT AKSES PER SITE ===")
    # for site in SITES_TO_GRANT:
    #     if site["site_id"]:
    #         grant_app_to_site(token, site["site_id"], site["name"])
    #     else:
    #         print(f"  [skip] {site['name']} — site_id belum diisi")

if __name__ == "__main__":
    main()