#!/usr/bin/env python3
"""Fetch an arXiv paper: metadata, LaTeX source (preferred) and PDF text.

Usage:
    python3 -I fetch_arxiv.py <arxiv-id-or-url> [--out DIR]

Output layout (DIR defaults to ./arxiv-papers/<id>):
    meta.json        title, authors, abstract, categories, dates, links
    source/          extracted LaTeX source (if the paper provides it)
    main.tex         best guess at the main .tex file, with \\input/\\include inlined
    paper.pdf        the PDF
    paper.txt        pdftotext output (fallback when LaTeX is unavailable)

Only the Python standard library is used. pdftotext (poppler) is optional.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "personal-agent-asset/arxiv-paper-reader (mailto:noreply@example.com)"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

ID_RE = re.compile(
    r"(?P<id>(\d{4}\.\d{4,5})|([a-z\-]+(\.[A-Z]{2})?/\d{7}))(?P<ver>v\d+)?",
    re.IGNORECASE,
)


def parse_id(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^https?://(www\.|export\.)?arxiv\.org/(abs|pdf|html|e-print|src)/", "", raw)
    raw = re.sub(r"\.pdf$", "", raw)
    m = ID_RE.search(raw)
    if not m:
        sys.exit(f"error: cannot parse arXiv id from {raw!r}")
    return m.group("id") + (m.group("ver") or "")


def http_get(url: str, retries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def fetch_meta(aid: str) -> dict:
    xml = http_get(f"https://export.arxiv.org/api/query?id_list={aid}")
    entry = ET.fromstring(xml).find(f"{ATOM}entry")
    if entry is None or entry.find(f"{ATOM}title") is None:
        sys.exit(f"error: arXiv id {aid} not found")
    text = lambda tag: " ".join((entry.findtext(tag) or "").split())  # noqa: E731
    return {
        "id": aid,
        "title": text(f"{ATOM}title"),
        "authors": [" ".join((a.findtext(f"{ATOM}name") or "").split()) for a in entry.findall(f"{ATOM}author")],
        "abstract": text(f"{ATOM}summary"),
        "published": text(f"{ATOM}published"),
        "updated": text(f"{ATOM}updated"),
        "primary_category": getattr(entry.find(f"{ARXIV_NS}primary_category"), "attrib", {}).get("term"),
        "categories": [c.get("term") for c in entry.findall(f"{ATOM}category")],
        "comment": text(f"{ARXIV_NS}comment") or None,
        "abs_url": f"https://arxiv.org/abs/{aid}",
        "pdf_url": f"https://arxiv.org/pdf/{aid}",
    }


def safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    dest = dest.resolve()
    for m in tar.getmembers():
        target = (dest / m.name).resolve()
        if not str(target).startswith(str(dest) + os.sep) and target != dest:
            continue  # path traversal
        if m.issym() or m.islnk() or m.isdev():
            continue
        if m.isdir():
            target.mkdir(parents=True, exist_ok=True)
        elif m.isfile():
            target.parent.mkdir(parents=True, exist_ok=True)
            f = tar.extractfile(m)
            if f is not None:
                target.write_bytes(f.read())


def fetch_source(aid: str, out: Path) -> bool:
    try:
        blob = http_get(f"https://arxiv.org/e-print/{aid}")
    except RuntimeError as e:
        print(f"warn: source unavailable: {e}", file=sys.stderr)
        return False
    src = out / "source"
    shutil.rmtree(src, ignore_errors=True)
    src.mkdir(parents=True)

    if blob[:4] == b"%PDF":
        return False  # author only uploaded a PDF
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as tar:
            safe_extract(tar, src)
        return any(src.rglob("*.tex"))
    except tarfile.TarError:
        pass
    try:  # single gzipped .tex file
        data = gzip.decompress(blob)
    except OSError:
        data = blob
    if b"\\documentclass" in data or b"\\begin{document}" in data:
        (src / "main.tex").write_bytes(data)
        return True
    return False


def find_main_tex(src: Path) -> Path | None:
    cands = []
    for p in src.rglob("*.tex"):
        try:
            t = p.read_text(errors="ignore")
        except OSError:
            continue
        if "\\documentclass" in t:
            score = ("\\begin{document}" in t) * 10 + len(t) / 1e6
            cands.append((score, p))
    return max(cands)[1] if cands else None


INPUT_RE = re.compile(r"\\(input|include|subfile)\s*\{([^}]+)\}")


def inline_inputs(path: Path, root: Path, depth: int = 0, seen: set | None = None) -> str:
    seen = seen if seen is not None else set()
    if depth > 10 or path in seen:
        return ""
    seen.add(path)
    text = path.read_text(errors="ignore")
    # drop full-line comments to cut noise
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("%"))

    def repl(m: re.Match) -> str:
        name = m.group(2).strip()
        for cand in (root / name, root / f"{name}.tex", path.parent / name, path.parent / f"{name}.tex"):
            if cand.is_file():
                return f"\n% ---- begin {name} ----\n{inline_inputs(cand, root, depth + 1, seen)}\n% ---- end {name} ----\n"
        return m.group(0)

    return INPUT_RE.sub(repl, text)


def fetch_pdf(aid: str, out: Path) -> None:
    pdf = out / "paper.pdf"
    pdf.write_bytes(http_get(f"https://arxiv.org/pdf/{aid}"))
    if shutil.which("pdftotext"):
        subprocess.run(["pdftotext", "-layout", str(pdf), str(out / "paper.txt")], check=False)
    else:
        print("warn: pdftotext not found; read paper.pdf directly", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper", help="arXiv id (2006.11239, 2006.11239v2) or abs/pdf URL")
    ap.add_argument("--out", help="output directory (default: ./arxiv-papers/<id>)")
    ap.add_argument("--no-pdf", action="store_true", help="skip PDF download")
    args = ap.parse_args()

    aid = parse_id(args.paper)
    out = Path(args.out or Path("arxiv-papers") / aid.replace("/", "_")).resolve()
    out.mkdir(parents=True, exist_ok=True)

    meta = fetch_meta(aid)
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"title: {meta['title']}")

    has_tex = fetch_source(aid, out)
    if has_tex:
        main_tex = find_main_tex(out / "source")
        if main_tex:
            (out / "main.tex").write_text(inline_inputs(main_tex, out / "source"))
            meta["main_tex"] = str(main_tex.relative_to(out))
    if not args.no_pdf:
        fetch_pdf(aid, out)

    meta.update(has_latex=has_tex, out_dir=str(out))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps({k: meta[k] for k in ("id", "title", "has_latex", "out_dir")}, ensure_ascii=False, indent=2))
    print("files:", ", ".join(sorted(p.name for p in out.iterdir())))


if __name__ == "__main__":
    main()
