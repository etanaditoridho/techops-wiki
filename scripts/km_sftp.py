"""
TechOpsKM — SFTP Uploader
Upload wiki MD files ke SFTP server Etana.
Dipanggil oleh km_processor.py setelah wiki di-generate.
"""
from dotenv import load_dotenv
load_dotenv()


import os
import paramiko
from pathlib import Path

# ============================================================
# CONFIG — isi SFTP_PASSWORD via environment variable
# ============================================================
SFTP_HOST     = "renodoc.asiatirtapharma.com"
SFTP_PORT     = 7235
SFTP_USERNAME = "aikms"
SFTP_PASSWORD = os.environ["SFTP_PASSWORD"]
SFTP_BASE     = "/sop/aikms"
SFTP_RAW_PATH = "/sop/aikms/raw"
SFTP_PATH     = "/sop/aikms/raw"  # fallback

# ============================================================
# CONNECT
# ============================================================
def get_sftp():
    """Buat koneksi SFTP dan return client"""
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

# ============================================================
# ENSURE REMOTE DIR EXISTS
# ============================================================
def ensure_remote_dir(sftp, remote_path):
    """Buat folder di SFTP kalau belum ada — pakai string split bukan Path()"""
    parts = [p for p in remote_path.split("/") if p]
    current = ""
    for part in parts:
        current = current + "/" + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            try:
                sftp.mkdir(current)
            except Exception:
                pass

# ============================================================
# UPLOAD FILE
# ============================================================
def upload_file(local_path, remote_filename=None, dept_folder=None):
    """
    Upload satu file MD ke SFTP server.
    local_path      : Path object ke file lokal
    remote_filename : nama file di SFTP (default: sama dengan lokal)
    dept_folder     : nama folder departemen dari SharePoint (misal: "Departement Engineering")
                      kalau diisi, file diupload ke /sop/aikms/raw/{dept_folder}/
                      kalau None, upload ke /sop/aikms/raw/
    """
    local_path      = Path(local_path)
    remote_filename = remote_filename or local_path.name

    # Tentukan remote folder
    if dept_folder:
        remote_folder = f"{SFTP_RAW_PATH}/{dept_folder}"
    else:
        remote_folder = SFTP_RAW_PATH

    remote_path = f"{remote_folder}/{remote_filename}"

    sftp, transport = get_sftp()
    try:
        ensure_remote_dir(sftp, remote_folder)
        sftp.put(str(local_path), remote_path)
        size = local_path.stat().st_size
        print(f"[SFTP] ✓ Uploaded: {remote_filename} ({size // 1024} KB) → {remote_path}")
        return True, size
    except Exception as e:
        print(f"[SFTP] ✗ Upload failed: {remote_filename} — {e}")
        return False, 0
    finally:
        sftp.close()
        transport.close()

# ============================================================
# UPLOAD BATCH
# ============================================================
def upload_batch(local_paths):
    """
    Upload multiple MD files sekaligus.
    local_paths : list of Path objects
    Returns: (success_count, fail_count)
    """
    sftp, transport = get_sftp()
    success = 0
    failed  = 0
    try:
        ensure_remote_dir(sftp, SFTP_PATH)
        for local_path in local_paths:
            local_path    = Path(local_path)
            remote_path   = f"{SFTP_PATH.rstrip('/')}/{local_path.name}"
            try:
                sftp.put(str(local_path), remote_path)
                size = local_path.stat().st_size
                print(f"[SFTP] ✓ {local_path.name} ({size // 1024} KB)")
                success += 1
            except Exception as e:
                print(f"[SFTP] ✗ {local_path.name} — {e}")
                failed += 1
    finally:
        sftp.close()
        transport.close()
    return success, failed

# ============================================================
# LIST REMOTE FILES
# ============================================================
def list_remote_files():
    """List semua file yang ada di SFTP path"""
    sftp, transport = get_sftp()
    try:
        files = sftp.listdir(SFTP_BASE)
        return [f for f in files if f.endswith(".md")]
    except Exception as e:
        print(f"[SFTP] ✗ Cannot list remote: {e}")
        return []
    finally:
        sftp.close()
        transport.close()

# ============================================================
# TEST CONNECTION
# ============================================================
def test_connection():
    """Test koneksi SFTP — dipanggil dari km_test.py"""
    try:
        sftp, transport = get_sftp()
        files = sftp.listdir(SFTP_BASE)
        sftp.close()
        transport.close()
        return True, f"Connected — {len(files)} files at {SFTP_BASE}"
    except Exception as e:
        return False, str(e)

# ============================================================
# MAIN — test langsung
# ============================================================
if __name__ == "__main__":
    print("Testing SFTP connection...")
    print(f"  Host : {SFTP_HOST}:{SFTP_PORT}")
    print(f"  User : {SFTP_USERNAME}")
    print(f"  Path : {SFTP_BASE}")
    ok, msg = test_connection()
    print(f"  {'✓' if ok else '✗'} {msg}")
