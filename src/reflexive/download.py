from __future__ import annotations

import argparse
import hashlib
import importlib.resources
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .source_layout import display_path, source_root as source_source_root
from .title_metadata import normalize_title_key


DEFAULT_BASE_URL = "https://reflexive.banteg.xyz/"


@dataclass(frozen=True)
class InstallerRecord:
    file_name: str
    size_bytes: int
    sha256: str
    title: str | None


def default_output_root() -> Path:
    return source_source_root("rutracker")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest_records(manifest_path: Path | None = None) -> list[InstallerRecord]:
    if manifest_path is None:
        payload = importlib.resources.files("reflexive.data").joinpath("rutracker_download_manifest.json").read_text(
            encoding="utf-8"
        )
    else:
        payload = manifest_path.read_text(encoding="utf-8")
    report = json.loads(payload)
    records: list[InstallerRecord] = []
    for row in report["records"]:
        records.append(
            InstallerRecord(
                file_name=str(row["file_name"]),
                size_bytes=int(row["size_bytes"]),
                sha256=str(row["sha256"]),
                title=str(row["title"]) if row.get("title") is not None else None,
            )
        )
    return records


def resolve_record(query: str, records: list[InstallerRecord]) -> InstallerRecord:
    exact_by_filename = {record.file_name.casefold(): record for record in records}
    exact = exact_by_filename.get(query.casefold())
    if exact is not None:
        return exact

    normalized = normalize_title_key(query)
    matches = [
        record
        for record in records
        if normalize_title_key(record.file_name) == normalized
        or (record.title is not None and normalize_title_key(record.title) == normalized)
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        options = ", ".join(record.file_name for record in matches[:10])
        raise ValueError(f"query is ambiguous; matches: {options}")

    suggestions = [
        record
        for record in records
        if normalized in normalize_title_key(record.file_name)
        or (record.title is not None and normalized in normalize_title_key(record.title))
    ]
    if suggestions:
        options = ", ".join(record.file_name for record in suggestions[:10])
        raise ValueError(f"no exact match for {query!r}; close matches: {options}")
    raise ValueError(f"no installer match for {query!r}")


def download_record(
    record: InstallerRecord,
    *,
    base_url: str,
    output_path: Path,
    force: bool,
) -> str:
    if output_path.exists():
        existing_size = output_path.stat().st_size
        existing_sha256 = sha256_file(output_path)
        if existing_size == record.size_bytes and existing_sha256 == record.sha256:
            return "already_present"
        if not force:
            raise FileExistsError(f"{display_path(output_path)} exists but does not match the expected installer; pass --force")
        output_path.unlink()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + ".part")
    if temp_path.exists():
        temp_path.unlink()

    url = urllib.parse.urljoin(base_url, urllib.parse.quote(record.file_name))
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; reflexive downloader)",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(request) as response, temp_path.open("wb") as handle:
            status = response.getcode()
            if status is not None and status >= 400:
                raise RuntimeError(f"mirror returned HTTP {status} for {url}")
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)

        size = temp_path.stat().st_size
        sha256 = sha256_file(temp_path)
        if size != record.size_bytes:
            raise ValueError(
                f"downloaded size mismatch for {record.file_name}: expected {record.size_bytes}, got {size}"
            )
        if sha256 != record.sha256:
            raise ValueError(
                f"downloaded SHA-256 mismatch for {record.file_name}: expected {record.sha256}, got {sha256}"
            )
        temp_path.replace(output_path)
        return "downloaded"
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a single original Reflexive installer from the mirror."
    )
    parser.add_argument("query", help="Exact installer filename or game title")
    parser.add_argument(
        "output_path",
        nargs="?",
        type=Path,
        default=None,
        help="Installer output path. Defaults to artifacts/sources/rutracker/<installer>.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Mirror base URL. Defaults to {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=None,
        help="Override the packaged download manifest JSON.",
    )
    parser.add_argument("--force", action="store_true", help="Replace a mismatched existing output file.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_path = args.manifest_path.resolve() if args.manifest_path is not None else None
    records = load_manifest_records(manifest_path)
    record = resolve_record(args.query, records)

    output_path = args.output_path.resolve() if args.output_path is not None else default_output_root() / record.file_name
    output_path = output_path.resolve()
    status = download_record(record, base_url=args.base_url, output_path=output_path, force=args.force)

    print(f"query={args.query}")
    if record.title is not None:
        print(f"title={record.title}")
    print(f"file_name={record.file_name}")
    print(f"url={urllib.parse.urljoin(args.base_url, urllib.parse.quote(record.file_name))}")
    print(f"output={display_path(output_path)}")
    print(f"size_bytes={record.size_bytes}")
    print(f"sha256={record.sha256}")
    print(f"status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
