"""
HTML table extractor for NASA SST-SOA chapter pages.

Handles:
- Titled tables (first row is a colspan cell with "Table N-N: ...")
- Rowspan expansion (manufacturer cells spanning multiple product rows)
- Units rows (second tbody row like [mN], [s], [kN-s] — skipped)
- Subgroup separator rows (full-width row dividing a table into named sections)
- Footnote rows (full-width row starting with *, †, Note, TRL, etc.)
- Continuation tables ("Table N-N (cont.):...") — merged into the base table
- Reference list extraction from the bottom of the page
"""

import re
import unicodedata

from bs4 import BeautifulSoup, Tag

# Matches "Table 4-7", "Table 4‑7" (non-breaking hyphen), "Table 4–7" (en-dash)
TABLE_TITLE_RE = re.compile(r"Table\s+(\d+)\s*[-\u2011\u2013]\s*(\d+)", re.IGNORECASE)
CONT_RE = re.compile(r"\(cont\.?\)", re.IGNORECASE)

# Patterns that identify footnote rows (not real subgroups)
FOOTNOTE_PATTERNS = re.compile(
    r"^(\*|†|‡|§|Note\b|TRL\s+values|Bold\s+values|Shields-1\s+Exp|Data\s+unknown|"
    r"–\s*Represents|—\s*Represents|\u2013\s*Represents|\u2014\s*Represents)",
    re.IGNORECASE,
)

# Units row: most cells look like "[something]"
UNIT_CELL_RE = re.compile(r"^\s*\[.+\]\s*$")


def _clean_text(text: str) -> str:
    """Normalize whitespace and decode common HTML entities."""
    # Replace non-breaking spaces and zero-width chars
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _cell_text(cell: Tag) -> str:
    """Extract clean text from a BeautifulSoup cell, handling <sup> for country names."""
    # Render <sup> content in parentheses (e.g. manufacturer country superscripts)
    for sup in cell.find_all("sup"):
        sup.replace_with(f" ({sup.get_text(strip=True)})")
    return _clean_text(cell.get_text())


def _is_units_row(cells: list[str], threshold: float = 0.5) -> bool:
    """Return True if the majority of cells look like unit annotations [N], [s], etc."""
    if not cells:
        return False
    unit_count = sum(1 for c in cells if UNIT_CELL_RE.match(c))
    return unit_count / len(cells) >= threshold


def _expand_rowspan(table: Tag, header_count: int) -> list[list[str]]:
    """
    Extract all data rows from a table, expanding rowspan cells.
    Returns a list of rows, each a list of strings with length == header_count.
    Skips the title row, column-header row, and units row automatically.
    """
    all_rows: list[list[str]] = []
    # carry[col_index] = (value, remaining_rows)
    carry: dict[int, tuple[str, int]] = {}

    tbody = table.find("tbody")
    if tbody:
        tr_list = tbody.find_all("tr", recursive=False)
    else:
        tr_list = table.find_all("tr")

    # Determine which rows to skip:
    # Row 0 in tbody is typically the column headers (strong tags).
    # Row 1 may be a units row.
    skip_indices: set[int] = set()
    for i, tr in enumerate(tr_list[:3]):
        cells = tr.find_all(["td", "th"])
        texts = [_cell_text(c) for c in cells]
        # Skip if it's the header row (most cells have <strong> children)
        strong_count = sum(1 for c in cells if c.find("strong"))
        if strong_count >= max(1, len(cells) * 0.4):
            skip_indices.add(i)
            continue
        # Skip units rows
        if _is_units_row(texts):
            skip_indices.add(i)

    for i, tr in enumerate(tr_list):
        if i in skip_indices:
            continue

        cells = tr.find_all(["td", "th"])

        # Single-cell colspan row = subgroup or footnote — handled by caller, not here
        if len(cells) == 1 and cells[0].get("colspan"):
            continue

        row: list[str] = []
        col_pos = 0
        cell_idx = 0

        while col_pos < header_count:
            # Fill from carry-forward buffer first
            if col_pos in carry:
                val, remaining = carry[col_pos]
                row.append(val)
                if remaining > 1:
                    carry[col_pos] = (val, remaining - 1)
                else:
                    del carry[col_pos]
                col_pos += 1
                continue

            if cell_idx >= len(cells):
                row.append("\u2013")  # en-dash for missing
                col_pos += 1
                continue

            cell = cells[cell_idx]
            cell_idx += 1
            value = _cell_text(cell)

            try:
                rowspan = int(cell.get("rowspan", 1))
            except (ValueError, TypeError):
                rowspan = 1
            try:
                colspan = int(cell.get("colspan", 1))
            except (ValueError, TypeError):
                colspan = 1

            for c_offset in range(colspan):
                actual_col = col_pos + c_offset
                row.append(value)
                if rowspan > 1 and actual_col < header_count:
                    carry[actual_col] = (value, rowspan - 1)

            col_pos += colspan

        if row:
            all_rows.append(row[:header_count])

    return all_rows


def _extract_column_headers(table: Tag) -> list[str]:
    """Find the column header row (cells with <strong> tags) in the table body."""
    tbody = table.find("tbody")
    rows = tbody.find_all("tr", recursive=False) if tbody else table.find_all("tr")

    for tr in rows[:4]:  # headers are always near the top
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        # Skip title row (single colspan cell)
        if len(cells) == 1 and cells[0].get("colspan"):
            continue
        strong_count = sum(1 for c in cells if c.find("strong"))
        if strong_count >= max(1, len(cells) * 0.4):
            return [_clean_text(c.get_text()) for c in cells]

    # Fallback: use first non-colspan row
    for tr in rows[:4]:
        cells = tr.find_all(["td", "th"])
        if cells and not (len(cells) == 1 and cells[0].get("colspan")):
            return [_clean_text(c.get_text()) for c in cells]

    return []


def _extract_subgroups_and_footnotes(
    table: Tag,
) -> tuple[list[tuple[int, str]], list[str]]:
    """
    Scan all rows and return:
    - subgroups: list of (row_index_in_tbody, subgroup_name)
    - footnotes: list of footnote strings

    row_index_in_tbody is used by the caller to split data into sections.
    """
    tbody = table.find("tbody")
    rows = tbody.find_all("tr", recursive=False) if tbody else table.find_all("tr")

    subgroups: list[tuple[int, str]] = []
    footnotes: list[str] = []

    for i, tr in enumerate(rows):
        cells = tr.find_all(["td", "th"])
        if len(cells) != 1:
            continue
        if not cells[0].get("colspan"):
            continue

        text = _clean_text(cells[0].get_text())
        if not text or text.strip("\u2013\u2014\u2012\u2011- ") == "":
            continue
        if TABLE_TITLE_RE.search(text):
            continue  # This is the table title row itself

        if FOOTNOTE_PATTERNS.search(text):
            footnotes.append(text)
        else:
            subgroups.append((i, text))

    return subgroups, footnotes


def _split_rows_by_subgroup(
    table: Tag,
    subgroups: list[tuple[int, str]],
    header_count: int,
) -> dict[str, list[list[str]]]:
    """
    Given the subgroup row indices, split the table body rows into sections.
    Returns dict of {subgroup_name: [rows]}.
    """
    tbody = table.find("tbody")
    all_tr = tbody.find_all("tr", recursive=False) if tbody else table.find_all("tr")

    # Determine skip rows (header, units)
    skip_indices: set[int] = set()
    for i, tr in enumerate(all_tr[:3]):
        cells = tr.find_all(["td", "th"])
        texts = [_cell_text(c) for c in cells]
        strong_count = sum(1 for c in cells if c.find("strong"))
        if strong_count >= max(1, len(cells) * 0.4):
            skip_indices.add(i)
            continue
        if _is_units_row(texts):
            skip_indices.add(i)

    # Build index of subgroup start positions
    subgroup_indices = [idx for idx, _ in subgroups]
    subgroup_names = [name for _, name in subgroups]

    sections: dict[str, list[list[str]]] = {}
    current_section = "__before_first_subgroup__"
    carry: dict[int, tuple[str, int]] = {}

    for row_i, tr in enumerate(all_tr):
        # Check if this row is a subgroup separator
        if row_i in subgroup_indices:
            sg_name = subgroup_names[subgroup_indices.index(row_i)]
            # A "(cont.)" subgroup is a continuation of the previous section —
            # keep current_section unchanged so rows merge into the same bucket.
            if not CONT_RE.search(sg_name):
                current_section = sg_name
                carry = {}  # reset rowspan carry at section boundaries
            continue

        if row_i in skip_indices:
            continue

        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        # Skip single colspan rows (footnotes etc.)
        if len(cells) == 1 and cells[0].get("colspan"):
            continue

        # Expand this row with rowspan carry
        row: list[str] = []
        col_pos = 0
        cell_idx = 0

        while col_pos < header_count:
            if col_pos in carry:
                val, remaining = carry[col_pos]
                row.append(val)
                if remaining > 1:
                    carry[col_pos] = (val, remaining - 1)
                else:
                    del carry[col_pos]
                col_pos += 1
                continue

            if cell_idx >= len(cells):
                row.append("\u2013")
                col_pos += 1
                continue

            cell = cells[cell_idx]
            cell_idx += 1
            value = _cell_text(cell)

            try:
                rowspan = int(cell.get("rowspan", 1))
            except (ValueError, TypeError):
                rowspan = 1
            try:
                colspan = int(cell.get("colspan", 1))
            except (ValueError, TypeError):
                colspan = 1

            for c_offset in range(colspan):
                actual_col = col_pos + c_offset
                row.append(value)
                if rowspan > 1 and actual_col < header_count:
                    carry[actual_col] = (value, rowspan - 1)

            col_pos += colspan

        if row:
            sections.setdefault(current_section, []).append(row[:header_count])

    # Drop any rows accumulated before the first subgroup
    sections.pop("__before_first_subgroup__", None)

    return sections


def extract_tables(html: str, chapter_config) -> list[dict]:
    """
    Parse a chapter page HTML and return a list of table dicts ready for JSON output.

    Each dict has keys: table_id, subgroup (optional), title, chapter_num,
    chapter_title, source_url, edition, columns, _notes, data.

    If a table has subgroups, multiple dicts are returned (one per subgroup).
    """
    soup = BeautifulSoup(html, "html.parser")
    raw_tables = soup.find_all("table")

    # --- Pass 1: collect all titled tables (including cont.) ---
    titled: list[dict] = []  # {table_id, title_raw, html_table, is_cont}

    for tbl in raw_tables:
        # Search first 3 rows for the title (some tables have a blank first row)
        all_tr_top = tbl.find_all("tr")[:3]
        title_cell = None
        for tr in all_tr_top:
            for cell in tr.find_all(["th", "td"]):
                if cell.get("colspan") and TABLE_TITLE_RE.search(cell.get_text()):
                    title_cell = cell
                    break
            if title_cell:
                break
        if title_cell is None:
            continue

        title_raw = _clean_text(title_cell.get_text())
        m = TABLE_TITLE_RE.search(title_raw)
        if not m:
            continue

        table_id = f"{m.group(1)}-{m.group(2)}"
        is_cont = bool(CONT_RE.search(title_raw))

        titled.append(
            {
                "table_id": table_id,
                "title_raw": title_raw,
                "html_table": tbl,
                "is_cont": is_cont,
            }
        )

    # --- Pass 2: merge cont. tables ---
    merged: list[dict] = []
    base_index: dict[str, int] = {}  # table_id -> index in merged

    for item in titled:
        tid = item["table_id"]
        if item["is_cont"] and tid in base_index:
            # Append rows to the base table's HTML by collecting extra rows
            base = merged[base_index[tid]]
            base["cont_tables"] = base.get("cont_tables", []) + [item["html_table"]]
        else:
            base_index[tid] = len(merged)
            item.setdefault("cont_tables", [])
            merged.append(item)

    # --- Pass 3: extract column headers, subgroups, footnotes, data ---
    results: list[dict] = []

    for item in merged:
        tbl = item["html_table"]
        cont_tables: list[Tag] = item.get("cont_tables", [])

        # Extract title (text after the colon)
        title_raw = item["title_raw"]
        colon_pos = title_raw.find(":")
        title = title_raw[colon_pos + 1:].strip() if colon_pos != -1 else title_raw

        # Strip "(cont.)" residue from title
        title = CONT_RE.sub("", title).strip(" :-")

        headers = _extract_column_headers(tbl)
        if not headers:
            continue
        n_cols = len(headers)

        subgroups, footnotes = _extract_subgroups_and_footnotes(tbl)

        # Collect footnotes from cont. tables too
        for ct in cont_tables:
            _, ct_footnotes = _extract_subgroups_and_footnotes(ct)
            footnotes.extend(ct_footnotes)

        # Deduplicate footnotes
        seen = set()
        unique_footnotes = []
        for f in footnotes:
            if f not in seen:
                seen.add(f)
                unique_footnotes.append(f)

        base_meta = {
            "table_id": item["table_id"],
            "title": title,
            "chapter_num": chapter_config.chapter_num,
            "chapter_title": chapter_config.title,
            "source_url": chapter_config.url,
            "edition": "2024",
            "columns": headers,
            "_notes": unique_footnotes,
        }

        if subgroups:
            # Split into one file per subgroup
            sections = _split_rows_by_subgroup(tbl, subgroups, n_cols)

            # Merge cont. table sections
            for ct in cont_tables:
                ct_subgroups, _ = _extract_subgroups_and_footnotes(ct)
                # Filter out cont. subgroups that are just "(cont.)" labels
                real_ct_subgroups = [
                    (i, name) for i, name in ct_subgroups
                    if not CONT_RE.search(name)
                ]
                if real_ct_subgroups:
                    ct_sections = _split_rows_by_subgroup(ct, real_ct_subgroups, n_cols)
                    for sg_name, sg_rows in ct_sections.items():
                        sections.setdefault(sg_name, []).extend(sg_rows)
                else:
                    # Cont. table has no real subgroups — append rows to last section
                    ct_rows = _expand_rowspan(ct, n_cols)
                    last_key = list(sections.keys())[-1] if sections else None
                    if last_key:
                        sections[last_key].extend(ct_rows)

            # Safety fallback: if splitting produced empty sections (e.g. note-row at
            # bottom of table was misidentified as subgroup), treat as a single table
            if not sections:
                rows = _expand_rowspan(tbl, n_cols)
                for ct in cont_tables:
                    rows.extend(_expand_rowspan(ct, n_cols))
                entry = dict(base_meta)
                # Move false subgroup names to _notes
                entry["_notes"] = unique_footnotes + [name for _, name in subgroups]
                entry["data"] = [dict(zip(headers, row)) for row in rows]
                results.append(entry)
            else:
                for sg_name, rows in sections.items():
                    entry = dict(base_meta)
                    entry["subgroup"] = sg_name
                    entry["data"] = [dict(zip(headers, row)) for row in rows]
                    results.append(entry)
        else:
            # No subgroups — single file
            rows = _expand_rowspan(tbl, n_cols)
            for ct in cont_tables:
                rows.extend(_expand_rowspan(ct, n_cols))

            entry = dict(base_meta)
            entry["data"] = [dict(zip(headers, row)) for row in rows]
            results.append(entry)

    return results


def extract_references(html: str) -> list[str]:
    """
    Extract the numbered reference list from the bottom of a chapter page.
    Returns a list of strings like ["(1) Author, Title, URL", "(2) ..."].
    """
    soup = BeautifulSoup(html, "html.parser")
    refs: list[str] = []

    # NASA pages wrap references in <ol> or numbered <p> tags
    # Pattern 1: <ol> list (most chapters)
    for ol in soup.find_all("ol"):
        items = ol.find_all("li")
        if len(items) > 2:
            for i, li in enumerate(items, 1):
                text = _clean_text(li.get_text())
                if text:
                    refs.append(f"({i}) {text}")
            if refs:
                return refs

    # Pattern 2: paragraphs starting with (N)
    ref_re = re.compile(r"^\s*\((\d+)\)\s+")
    for p in soup.find_all("p"):
        text = _clean_text(p.get_text())
        if ref_re.match(text):
            refs.append(text)

    return refs
