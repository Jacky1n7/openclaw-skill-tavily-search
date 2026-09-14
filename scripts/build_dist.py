#!/usr/bin/env python3
import argparse
import hashlib
import io
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "tavily-search"
DIST_DIR = ROOT / "dist"
ARCHIVE_PATH = DIST_DIR / "tavily-search.skill"
MANIFEST_PATH = DIST_DIR / "tavily-search.manifest.json"
FILES = ("SKILL.md", "scripts/tavily_search.py")


def file_digest(data):
    return hashlib.sha256(data).hexdigest()


def skill_version(skill_text):
    match = re.search(r"^\s*version:\s*['\"]?([^'\"\s]+)", skill_text, re.MULTILINE)
    if not match:
        raise ValueError("SKILL.md frontmatter must declare a version")
    return match.group(1)


def build_outputs():
    contents = {path: (SKILL_DIR / path).read_bytes() for path in FILES}
    version = skill_version(contents["SKILL.md"].decode("utf-8"))
    manifest = {
        "version": version,
        "files": [
            {
                "path": path,
                "sha256": file_digest(contents[path]),
                "bytes": len(contents[path]),
            }
            for path in FILES
        ],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(
        archive_buffer, "w", compression=zipfile.ZIP_STORED
    ) as archive:
        for path in FILES:
            info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, contents[path])
    return archive_buffer.getvalue(), manifest_bytes


def main():
    parser = argparse.ArgumentParser(
        description="Build deterministic Tavily Search skill assets"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    archive, manifest = build_outputs()

    if args.check:
        stale = []
        if not ARCHIVE_PATH.exists() or ARCHIVE_PATH.read_bytes() != archive:
            stale.append(str(ARCHIVE_PATH.relative_to(ROOT)))
        if not MANIFEST_PATH.exists() or MANIFEST_PATH.read_bytes() != manifest:
            stale.append(str(MANIFEST_PATH.relative_to(ROOT)))
        if stale:
            print("Generated files are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        return 0

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_PATH.write_bytes(archive)
    MANIFEST_PATH.write_bytes(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
