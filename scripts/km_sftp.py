"""
TechOpsKM SFTP uploader.
Upload markdown dan artifact knowledge ke SFTP server Etana.
Dipanggil oleh pipeline wiki setelah file di-generate.
"""

from dotenv import load_dotenv

load_dotenv()

import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import paramiko


SFTP_HOST = "renodoc.asiatirtapharma.com"
SFTP_PORT = 7235
SFTP_USERNAME = "aikms"
SFTP_PASSWORD = os.environ["SFTP_PASSWORD"]
SFTP_BASE = "/sop/aikms"
SFTP_RAW_PATH = "/sop/aikms/raw"
SFTP_PATH = "/sop/aikms/raw"  # fallback legacy batch upload path

REGISTRY_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "techopskm"
    / "backend"
    / "scripts"
    / "upsert_markdown_registry_entry.js"
)
ENABLE_REGISTRY_SYNC = os.environ.get("KM_ENABLE_REGISTRY_SYNC", "false").strip().lower() == "true"


def get_sftp():
    """Buat koneksi SFTP dan return (sftp, transport)."""
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport


def ensure_remote_dir(sftp, remote_path):
    """Buat folder remote secara rekursif kalau belum ada."""
    parts = [p for p in str(remote_path).split("/") if p]
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


def sync_markdown_registry(remote_path, size):
    """
    Best-effort hook ke registry DB.
    Tidak boleh menggagalkan upload utama kalau sinkronisasi metadata gagal.
    """
    remote_path = str(remote_path).replace("\\", "/")
    if not remote_path.lower().endswith(".md"):
        return
    if not ENABLE_REGISTRY_SYNC:
        return

    node_bin = shutil.which("node")
    if not node_bin:
        print("[SFTP] ! Registry sync skipped: node not found")
        return
    if not REGISTRY_SCRIPT.exists():
        print(f"[SFTP] ! Registry sync skipped: script not found at {REGISTRY_SCRIPT}")
        return

    cmd = [
        node_bin,
        str(REGISTRY_SCRIPT),
        "--path",
        remote_path,
        "--size",
        str(size or 0),
        "--remoteModifiedAt",
        datetime.now(timezone.utc).isoformat(),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(REGISTRY_SCRIPT.parent.parent),
        )
        stdout = (result.stdout or "").strip()
        if stdout:
            print(f"[SFTP] ! Registry sync ok: {stdout}")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or str(exc)
        print(f"[SFTP] ! Registry sync failed: {detail}")


def upload_file(local_path, remote_filename=None, dept_folder=None):
    """
    Upload satu file ke SFTP.
    Kalau dept_folder diisi, target jadi /sop/aikms/raw/{dept_folder}/.
    """
    local_path = Path(local_path)
    remote_filename = remote_filename or local_path.name

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
        print(f"[SFTP] OK Uploaded: {remote_filename} ({size // 1024} KB) -> {remote_path}")
        sync_markdown_registry(remote_path, size)
        return True, size
    except Exception as e:
        print(f"[SFTP] FAIL Upload failed: {remote_filename} - {e}")
        return False, 0
    finally:
        sftp.close()
        transport.close()


def upload_to_path(local_path, remote_path):
    """Upload file ke remote path arbitrary di SFTP."""
    local_path = Path(local_path)
    remote_path = str(remote_path).replace("\\", "/")
    remote_folder = remote_path.rsplit("/", 1)[0]

    sftp, transport = get_sftp()
    try:
        ensure_remote_dir(sftp, remote_folder)
        sftp.put(str(local_path), remote_path)
        size = local_path.stat().st_size
        print(f"[SFTP] OK Uploaded: {local_path.name} ({size // 1024} KB) -> {remote_path}")
        sync_markdown_registry(remote_path, size)
        return True, size
    except Exception as e:
        print(f"[SFTP] FAIL Upload failed: {local_path.name} - {e}")
        return False, 0
    finally:
        sftp.close()
        transport.close()


def upload_batch(local_paths):
    """Upload multiple markdown files sekaligus ke path fallback legacy."""
    sftp, transport = get_sftp()
    success = 0
    failed = 0
    try:
        ensure_remote_dir(sftp, SFTP_PATH)
        for local_path in local_paths:
            local_path = Path(local_path)
            remote_path = f"{SFTP_PATH.rstrip('/')}/{local_path.name}"
            try:
                sftp.put(str(local_path), remote_path)
                size = local_path.stat().st_size
                print(f"[SFTP] OK {local_path.name} ({size // 1024} KB)")
                sync_markdown_registry(remote_path, size)
                success += 1
            except Exception as e:
                print(f"[SFTP] FAIL {local_path.name} - {e}")
                failed += 1
    finally:
        sftp.close()
        transport.close()
    return success, failed


def list_remote_files():
    """List file markdown di root base path."""
    sftp, transport = get_sftp()
    try:
        files = sftp.listdir(SFTP_BASE)
        return [f for f in files if f.endswith(".md")]
    except Exception as e:
        print(f"[SFTP] FAIL Cannot list remote: {e}")
        return []
    finally:
        sftp.close()
        transport.close()


def test_connection():
    """Test koneksi SFTP."""
    try:
        sftp, transport = get_sftp()
        files = sftp.listdir(SFTP_BASE)
        sftp.close()
        transport.close()
        return True, f"Connected - {len(files)} files at {SFTP_BASE}"
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    print("Testing SFTP connection...")
    print(f"  Host : {SFTP_HOST}:{SFTP_PORT}")
    print(f"  User : {SFTP_USERNAME}")
    print(f"  Path : {SFTP_BASE}")
    ok, msg = test_connection()
    print(f"  {'OK' if ok else 'FAIL'} {msg}")
