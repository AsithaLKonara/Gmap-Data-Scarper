from __future__ import annotations

import csv
import os
from typing import Dict, Iterable, List


def _ensure_parent_dir(path: str) -> None:
	parent = os.path.dirname(os.path.expanduser(path))
	if parent and not os.path.exists(parent):
		os.makedirs(parent, exist_ok=True)


def write_row_incremental(csv_path: str, header: List[str], row: Dict[str, str]) -> None:
	"""Append a row to CSV, creating file with header if needed."""
	csv_path = os.path.expanduser(csv_path)
	_ensure_parent_dir(csv_path)
	file_exists = os.path.exists(csv_path)
	with open(csv_path, "a", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
		if not file_exists:
			writer.writeheader()
		writer.writerow(row)


def write_rows_incremental(csv_path: str, header: List[str], rows: Iterable[Dict[str, str]]) -> None:
	for r in rows:
		write_row_incremental(csv_path, header, r)


