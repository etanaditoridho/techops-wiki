from pathlib import Path
import subprocess
import sys

# Root vault
ROOT = Path(r"C:\Dito\Digitalization\TechOpsKM\techops-wiki")

# Existing folders - keep current setup safe
RAW_DIR = ROOT / "raw"
WIKI_DIR = ROOT / "wiki"

# File extensions to convert
SUPPORTED_EXTENSIONS = {".docx"}

def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def convert_docx_to_markdown(input_file: Path, output_file: Path) -> bool:
    """
    Convert a DOCX file to Markdown using Pandoc.
    Returns True if conversion succeeds, otherwise False.
    """
    ensure_folder(output_file.parent)

    command = [
        "pandoc",
        str(input_file),
        "-f", "docx",
        "-t", "gfm",
        "-o", str(output_file),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to convert: {input_file.name}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("[ERROR] Pandoc not found. Make sure Pandoc is installed and available in PATH.")
        return False

def main() -> int:
    if not RAW_DIR.exists():
        print(f"[ERROR] Raw folder not found: {RAW_DIR}")
        return 1

    ensure_folder(WIKI_DIR)

    files = [f for f in RAW_DIR.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        print("[INFO] No DOCX files found in raw/.")
        return 0

    success_count = 0
    fail_count = 0

    for input_file in files:
        output_file = WIKI_DIR / f"{input_file.stem}.md"
        print(f"[INFO] Converting {input_file.name} -> {output_file.name}")

        if convert_docx_to_markdown(input_file, output_file):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n[DONE] Success: {success_count}, Failed: {fail_count}")
    return 0 if fail_count == 0 else 2

if __name__ == "__main__":
    sys.exit(main())