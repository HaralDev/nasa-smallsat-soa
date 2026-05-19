"""
NASA SST-SOA scraper — main entry point.

Usage:
    python scraper/scrape.py [--chapters 2,3,4] [--cache] [--output-dir .]

Fetches each chapter page, extracts all tables as JSON files, and writes
per-folder README.md files with the chapter reference list.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.config import CHAPTERS, EDITION, ChapterConfig
from scraper.extractor import extract_references, extract_tables

SCRAPE_DATE = date.today().isoformat()
CACHE_DIR = Path(__file__).parent / ".cache"

# Table type classification for README display. Keyed by NASA table_id and
# curated for the 2026 edition (NASA renumbers tables between editions, so this
# map must be reviewed whenever EDITION is bumped).
# "products"      — rows are commercial/organizational products or services with specs
# "specifications" — reference data, standards, design parameters (not specific products)
# "reference"     — overview/summary/comparison tables, not specific products
#
# NASA's 2026 pages reuse some table numbers for two different tables (e.g.
# "Table 4-1" labels both the propulsion summary and the hydrazine table;
# "Table 6-7" labels both robotic arms and PLA filaments). The type below
# reflects the legitimately numbered table for that id; the duplicate inherits
# it. See the "Known Limitations" section of README.md.
TABLE_TYPES: dict[str, str] = {
    # Chapter 2 — Platforms
    "2-1": "products", "2-2": "products", "2-3": "products", "2-4": "products",
    "2-5": "products", "2-6": "products", "2-7": "products", "2-8": "reference",
    "2-9": "reference",
    # Chapter 3 — Power (3-9 removed in 2026)
    "3-1": "products", "3-2": "products", "3-3": "products", "3-4": "products",
    "3-5": "products", "3-6": "specifications", "3-7": "products", "3-8": "products",
    # Chapter 4 — Propulsion (4-2 not labeled in 2026; 4-1 also labels Hydrazine)
    "4-1": "reference", "4-3": "products", "4-4": "products",
    "4-5": "products", "4-6": "products", "4-7": "products", "4-8": "products",
    "4-9": "products", "4-10": "products", "4-11": "products", "4-12": "products",
    "4-13": "products",
    # Chapter 5 — GNC
    "5-1": "reference", "5-2": "products", "5-3": "products", "5-4": "products",
    "5-5": "products", "5-6": "products", "5-7": "products", "5-8": "products",
    "5-9": "products", "5-10": "products", "5-11": "products", "5-12": "products",
    "5-13": "products", "5-14": "reference",
    # Chapter 6 — Structures (6-3 and 6-17 removed; 6-7 also labels PLA filaments)
    "6-1": "specifications", "6-2": "products", "6-4": "reference",
    "6-5": "products", "6-6": "products", "6-7": "products",
    "6-8": "products", "6-9": "products", "6-10": "products", "6-11": "products",
    "6-12": "products", "6-13": "products", "6-14": "products",
    "6-15": "specifications", "6-16": "specifications",
    # Chapter 7 — Thermal
    "7-1": "reference", "7-2": "reference", "7-3": "products", "7-4": "products",
    "7-5": "products", "7-6": "specifications", "7-7": "products", "7-8": "products",
    "7-9": "products", "7-10": "reference", "7-11": "products", "7-12": "products",
    "7-13": "products", "7-14": "products",
    # Chapter 8 — Avionics (expanded 2 -> 6 tables in 2026)
    "8-1": "specifications", "8-2": "specifications", "8-3": "reference",
    "8-4": "products", "8-5": "products", "8-6": "products",
    # Chapter 9 — Communications
    "9-1": "specifications", "9-2": "products", "9-3": "products",
    "9-4": "reference", "9-5": "reference",
    # Chapter 10 — Integration, Launch, Deployment (expanded 1 -> 4 tables)
    "10-1": "products", "10-2": "products", "10-3": "products", "10-4": "products",
    # Chapter 11 — Ground Data (11-17 removed in 2026)
    "11-1": "reference", "11-2": "specifications", "11-3": "specifications",
    "11-4": "specifications", "11-5": "specifications", "11-6": "reference",
    "11-7": "products", "11-8": "products", "11-9": "products",
    "11-10": "products", "11-11": "products", "11-12": "products",
    "11-13": "specifications", "11-14": "products", "11-15": "specifications",
    "11-16": "products",
    # Chapter 12 — ID & Tracking
    "12-1": "reference",
    # Chapter 13 — Deorbit
    "13-1": "reference", "13-2": "products", "13-3": "reference",
}

TABLE_TYPE_DESCRIPTIONS = {
    "products": "Products — rows are specific commercial or government products/services with technical specs",
    "specifications": "Specifications — design parameters, standards, or comparison data (not specific products)",
    "reference": "Reference — overview, summary, or classification table",
}

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "nasa-sst-soa-scraper/1.0 "
            "(github.com/your-org/nasa-smallsat-soa; educational use)"
        )
    }
)


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def fetch_html(url: str, use_cache: bool = False) -> str:
    slug = re.sub(r"[^a-z0-9_-]", "_", url.split("/")[-1] or url.split("/")[-2])
    cache_path = CACHE_DIR / f"{slug}.html"

    if use_cache and cache_path.exists():
        print(f"  [cache] {cache_path.name}")
        return cache_path.read_text(encoding="utf-8")

    print(f"  [fetch] {url}")
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text

    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(html, encoding="utf-8")

    return html


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

MAX_SLUG_LEN = 60


def _slugify(text: str, max_len: int = MAX_SLUG_LEN) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    if max_len:
        return text[:max_len].rstrip("_")
    return text


# Hardcoded short names for known long subgroup slugs
_SUBGROUP_SHORT = {
    "4_6_1chemical_propulsion_technologies": "chemical_propulsion",
    "4_6_2electric_propulsion_technologies": "electric_propulsion",
    "4_6_3propellantlesspropulsion_technologies": "propellantless_propulsion",
    "integrated_propulsion_systems": "integrated_systems",
    "thruster_heads": "thruster_heads",
    "thruster": "thruster_heads",
    "terrestrial_link_data_transport_capabilities": "terrestrial_link_data_transport",
    "spacecraft_navigation_tracking_capabilities": "spacecraft_navigation_tracking",
    "forward_command_communications": "forward_command",
    "return_telemetry_communications": "return_telemetry",
}

# Hardcoded short names for known long table title slugs
_TITLE_SHORT = {
    "state_of_the_art_hydrazine_monopropellant_devices_applicable_to_small_spacecraft": "hydrazine",
    "current_state_of_the_art_hydrazine_monopropellant_devices_applicable_to_small_spacecraft": "hydrazine",
    "current_state_of_the_art_in_other_mono_and_bipropellant_devices_applicable_to_small": "alt_monobiprop",
    "alternative_monopropellant_and_bipropellant_propulsion": "alt_monobiprop",
    "current_state_of_the_art_hybrid_devices_applicable_to_small_spacecraft": "hybrid",
    "hybrid_chemical_propulsion": "hybrid_chemical",
    "current_state_of_the_art_cold_gas_devices_applicable_to_small_spacecraft": "cold_gas",
    "cold_gas_propulsion": "cold_gas",
    "solid_motor_chemical_propulsion": "solid_motor",
    "electrothermal_electric_propulsion": "electrothermal",
    "electrospray_electric_propulsion": "electrospray",
    "gridded_ion_electric_propulsion": "gridded_ion",
    "hall_effect_electric_propulsion_thrusters": "hall_effect",
    "pulsed_plasma_and_vacuum_arc_electric_propulsion": "pulsed_plasma",
    "ambipolar_electric_propulsion": "ambipolar",
    "propellant_less_propulsion": "propellantless",
    "spacecraft_physical_dimension_and_weight_requirements_from_deployers": "deployer_requirements",
    "list_of_contact_information_for_organizations_in_this_chapter": "contact_information",
    "sample_of_highly_integrated_onboard_computing_systems": "onboard_computing_systems",
    "primary_elements_of_a_ground_system": "primary_elements",
    "nsn_direct_to_earth_command_and_telemetry_capabilities_per_frequency": "nsn_dte_capabilities",
    "dsn_customers_mission_characteristics_frequencies_and_services": "dsn_customers_and_services",
    "service_providers_for_space_relay_networks": "service_providers_space_relay",
    "service_providers_for_dte_ground_system_network": "service_providers_dte_ground",
    "projected_performance_of_legs_assets_pending_finalization": "projected_performance_legs",
    "mission_operations_and_scheduling_software": "mission_ops_and_scheduling",
    "european_optical_nucleus_network_ogs_key_parameters": "european_optical_nucleus_ogs",
    "shields_1_experimental_total_ionizing_dose_measurements_in_pleo": "shields_1_ionizing_dose",
    "xp_charge_dissipation_coating_and_commercial_conformal_coating_resistivity_comparisons": "xp_charge_dissipation_coating",
    "commercial_orbital_transfer_maneuvering_vehicles": "commercial_otv_omv",
    "select_frequency_bands_by_infostellar": "frequency_bands_infostellar",
    "nsn_supported_radio_frequencies_and_bandwidths": "nsn_supported_radio_frequencies",
    "bolted_joint_thermal_conductance_design_guideline": "bolted_joint_thermal_conductance",
    "thermal_interface_materials_and_conductive_gaskets": "thermal_interface_materials",
    "summary_of_propulsion_technologies_surveyed": "summary",
    "commercial_and_space_li_ion_manufacturers": "li_ion_manufacturers",
    "power_management_and_distribution_system_products": "power_management_and_distribution",
}


def _title_slug(title: str) -> str:
    # Strip parenthetical suffixes (long notes appended to some chapter 2+ titles)
    clean = title.split("(")[0].strip()
    # Look up in _TITLE_SHORT using the full (untruncated) slug first
    full_raw = _slugify(clean, max_len=0)
    if full_raw in _TITLE_SHORT:
        return _TITLE_SHORT[full_raw]
    return full_raw[:MAX_SLUG_LEN].rstrip("_")


def _subgroup_slug(subgroup: str) -> str:
    raw = _slugify(subgroup)
    return _SUBGROUP_SHORT.get(raw, raw[:MAX_SLUG_LEN])


def build_filename(table: dict) -> str:
    tid = table["table_id"]
    t_slug = _title_slug(table["title"])

    if "subgroup" in table:
        sg_slug = _subgroup_slug(table["subgroup"])
        return f"table_{tid}_{t_slug}_{sg_slug}.json"
    else:
        return f"table_{tid}_{t_slug}.json"


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------


def write_table_json(table: dict, output_dir: Path) -> Path:
    filename = build_filename(table)
    path = output_dir / filename

    # Add scrape_date and type now (runtime)
    payload = dict(table)
    payload["scrape_date"] = SCRAPE_DATE
    payload["type"] = TABLE_TYPES.get(table["table_id"], "reference")

    # Re-order keys for readability
    ordered_keys = [
        "table_id", "subgroup", "title", "chapter_num", "chapter_title",
        "source_url", "edition", "scrape_date", "type", "columns", "_notes", "data",
    ]
    out = {k: payload[k] for k in ordered_keys if k in payload}

    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_chapter_readme(
    chapter: ChapterConfig,
    tables: list[dict],
    references: list[str],
    output_dir: Path,
) -> None:
    lines = [
        f"# Chapter {chapter.chapter_num} \u2014 {chapter.title}",
        "",
        f"**Source:** {chapter.url}  ",
        f"**Edition:** {EDITION}  ",
        f"**Data scraped:** {SCRAPE_DATE}",
        "",
    ]

    if not tables:
        lines += [
            "No data tables are present in this chapter.",
            "",
        ]
    else:
        lines += [
            "## Files in this folder",
            "",
            "| File | NASA Table | Type | Subgroup |",
            "|------|-----------|------|---------|",
        ]
        for t in tables:
            fname = build_filename(t)
            table_label = f"Table {t['table_id']}: {t['title']}"
            ttype = TABLE_TYPES.get(t["table_id"], "reference")
            subgroup = t.get("subgroup", "\u2014")
            lines.append(f"| {fname} | {table_label} | {ttype} | {subgroup} |")
        lines.append("")

        # Table type legend
        used_types = {TABLE_TYPES.get(t["table_id"], "reference") for t in tables}
        if len(used_types) > 1:
            lines += ["**Table types:**", ""]
            for ttype, desc in TABLE_TYPE_DESCRIPTIONS.items():
                if ttype in used_types:
                    lines.append(f"- **{ttype}**: {desc.split(' — ')[1]}")
            lines.append("")

        # Notes on structure
        has_subgroups = any("subgroup" in t for t in tables)

        notes_lines = []
        # Find table IDs that were cont.-merged (known from analysis)
        known_cont = {"4-3", "4-10"}
        for tid in known_cont:
            if any(t["table_id"] == tid for t in tables):
                notes_lines.append(
                    f"- **Table {tid}**: The HTML source contained a \"(cont.)\" continuation "
                    f"section that has been merged into the relevant subgroup files."
                )

        if has_subgroups:
            notes_lines.append(
                "- **Subgroup splits**: Some tables contain full-width row separators that "
                "divide data into named sections (e.g., \"Integrated Propulsion Systems\" / "
                "\"Thruster Heads\"). Each section is stored as a separate JSON file. "
                "Files sharing the same `table_id` prefix belong to the same original table."
            )

        # Chapter-specific notes
        if chapter.chapter_num == 11:
            notes_lines.append(
                "- **Table 11-17** (European Optical Nucleus Network OGS Key Parameters): "
                "This table is published as a PNG image on the NASA page and cannot be "
                "extracted as structured data. It is not included in this folder."
            )

        if notes_lines:
            lines += ["## Notes on table structure", ""]
            lines += notes_lines
            lines.append("")

    if references:
        lines += ["## References", ""]
        lines += references
        lines.append("")

    readme_path = output_dir / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def scrape_chapter(
    chapter: ChapterConfig,
    repo_root: Path,
    use_cache: bool,
) -> list[dict]:
    output_dir = repo_root / chapter.output_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_html(chapter.url, use_cache=use_cache)
    tables = extract_tables(html, chapter)
    references = extract_references(html)

    written = []
    written_names: set[str] = set()
    for t in tables:
        path = write_table_json(t, output_dir)
        print(f"    wrote {path.name}  ({len(t['data'])} rows)")
        written.append(t)
        written_names.add(path.name)

    # Prune stale table files from previous editions. NASA renumbers and
    # renames tables between editions, so a file written last year may no
    # longer be produced this run. Remove any table_*.json in this chapter's
    # folder that the current scrape did not write, keeping the repo a clean
    # snapshot of a single edition.
    for stale in sorted(output_dir.glob("table_*.json")):
        if stale.name not in written_names:
            stale.unlink()
            print(f"    pruned {stale.name}  (stale, not in this edition)")

    write_chapter_readme(chapter, written, references, output_dir)
    print(f"    wrote README.md")

    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"Scrape NASA SST-SOA {EDITION} chapter pages into JSON files."
    )
    parser.add_argument(
        "--chapters",
        help="Comma-separated chapter numbers to scrape (default: all)",
        default=None,
    )
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Cache downloaded HTML in scraper/.cache/ for faster re-runs",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Root directory for output (default: repo root, auto-detected)",
    )
    args = parser.parse_args()

    # Determine repo root (parent of scraper/)
    repo_root = Path(args.output_dir) if args.output_dir else Path(__file__).parent.parent

    # Filter chapters
    if args.chapters:
        requested = {int(x.strip()) for x in args.chapters.split(",")}
        chapters = [c for c in CHAPTERS if c.chapter_num in requested]
    else:
        chapters = CHAPTERS

    total_tables = 0
    total_files = 0

    for i, chapter in enumerate(chapters):
        print(f"\nChapter {chapter.chapter_num}: {chapter.title}")
        tables = scrape_chapter(chapter, repo_root, use_cache=args.cache)
        total_tables += len({t["table_id"] for t in tables})
        total_files += len(tables)

        # Polite delay between requests
        if i < len(chapters) - 1:
            time.sleep(1)

    print(f"\nDone. {total_tables} unique tables -> {total_files} JSON files written.")


if __name__ == "__main__":
    main()
