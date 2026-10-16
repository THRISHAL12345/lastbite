#!/usr/bin/env python3
"""Prepare release values; does not push Git changes or contact a cluster."""
import argparse
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("owner", help="GitHub owner of the successfully scanned GHCR packages")
parser.add_argument("sha", help="Full 40-character source commit SHA from the successful CI run")
args = parser.parse_args()
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", args.owner):
    parser.error("Invalid GitHub owner")
if not re.fullmatch(r"[a-fA-F0-9]{40}", args.sha):
    parser.error("Use a full 40-character commit SHA")
root = Path(__file__).resolve().parents[1]
path = root / "helm/lastbite/values-release.yaml"
path.write_text("# Promote only after BOTH image scans and pushes succeed.\n" + "".join(
    f'{component}:\n  repository: ghcr.io/{args.owner.lower()}/lastbite-{component}\n  tag: "{args.sha.lower()}"\n'
    for component in ("backend", "frontend")
))
print(f"Prepared {path.relative_to(root)}. Review and commit this file to promote the release.")
