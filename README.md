# NASA Small Spacecraft Technology — State of the Art (SST-SOA)

Machine-readable data extracted from NASA's *State-of-the-Art of Small Spacecraft Technology* report, 2026 edition.

**Source:** [nasa.gov/smallsat-institute/sst-soa](https://www.nasa.gov/smallsat-institute/sst-soa/)  
**Edition:** 2026 &nbsp;·&nbsp; the previous **2024** edition is archived, unchanged, on the [`master-2024-report`](../../tree/master-2024-report) branch  
**Data scraped:** 2026-05-19  
**Format:** JSON (one file per table or table subgroup)

> **Attribution:** All data originates from NASA's Small Spacecraft Technology Program.  
> Original report: https://www.nasa.gov/smallsat-institute/sst-soa/  
> This repository is not affiliated with or endorsed by NASA.  
> NASA content is U.S. government work and is in the public domain.  
> The scraper code in this repository is released under the MIT License.

---

## What is the SST-SOA?

NASA publishes this report annually to document the current state of the art in small spacecraft (under ~180 kg) subsystem technologies. It covers 13 subsystem areas from complete spacecraft platforms to propulsion, power, communications, thermal control, and more. Each chapter surveys commercially and governmentally available hardware and technologies, organized in tabular form.

This repository extracts every data table from the 2026 edition into structured JSON files, making the data accessible for programmatic use, analysis, and AI applications.

---

## Repository Structure

```
nasa-smallsat-soa/
├── 01-introduction/                      (no tables)
├── 02-platforms/                         (9 JSON files)
├── 03-power-subsystems/                  (8 JSON files)
├── 04-in-space-propulsion/               (21 JSON files)
├── 05-guidance-navigation-and-control/   (14 JSON files)
├── 06-structures-materials-and-mechanisms/ (16 JSON files)
├── 07-thermal-control/                   (14 JSON files)
├── 08-small-spacecraft-avionics/         (6 JSON files)
├── 09-communications/                    (5 JSON files)
├── 10-integration-launch-and-deployment/ (4 JSON files)
├── 11-ground-data-systems-and-mission-operations/ (18 JSON files)
├── 12-identification-and-tracking-systems/ (1 JSON file)
├── 13-deorbit-systems/                   (3 JSON files)
├── scraper/                              (Python scraper)
└── README.md
```

Each chapter folder contains:
- One JSON file per table (or per table subgroup — see below)
- A `README.md` listing all files, table titles, table types, and the full chapter reference list

**Total: 119 JSON files** (107 unique NASA tables; some split into subgroup files) across 13 chapters.

---

## Chapter Index

| Chapter | Folder | Files | Topics |
|---------|--------|-------|--------|
| 1 | [01-introduction](01-introduction/) | — | Overview, no tables |
| 2 | [02-platforms](02-platforms/) | 9 | Complete spacecraft buses (CubeSat, ESPA-class, hosted payloads) |
| 3 | [03-power-subsystems](03-power-subsystems/) | 8 | Solar cells, batteries, PMAD |
| 4 | [04-in-space-propulsion](04-in-space-propulsion/) | 21 | Chemical, electric, propellantless propulsion |
| 5 | [05-guidance-navigation-and-control](05-guidance-navigation-and-control/) | 14 | Reaction wheels, star trackers, GPS, gyros |
| 6 | [06-structures-materials-and-mechanisms](06-structures-materials-and-mechanisms/) | 16 | Structures, deployers, AM materials, mechanisms |
| 7 | [07-thermal-control](07-thermal-control/) | 14 | Passive/active thermal systems, coatings, heat pipes |
| 8 | [08-small-spacecraft-avionics](08-small-spacecraft-avionics/) | 6 | Onboard computers, memory, AI applications, flight software, operating systems |
| 9 | [09-communications](09-communications/) | 5 | Antennas, radios, lasercom |
| 10 | [10-integration-launch-and-deployment](10-integration-launch-and-deployment/) | 4 | Small launch vehicles, dispensers/deployers, separation devices, orbital transfer/maneuvering vehicles |
| 11 | [11-ground-data-systems-and-mission-operations](11-ground-data-systems-and-mission-operations/) | 18 | Ground networks, mission ops software |
| 12 | [12-identification-and-tracking-systems](12-identification-and-tracking-systems/) | 1 | Tracking technologies |
| 13 | [13-deorbit-systems](13-deorbit-systems/) | 3 | Passive/active deorbit, drag sails |

---

## JSON File Format

Each JSON file represents one table or one named subgroup within a table.

### Standard table

```json
{
  "table_id": "13-2",
  "title": "Drag Sail Missions",
  "chapter_num": 13,
  "chapter_title": "Deorbit Systems",
  "source_url": "https://www.nasa.gov/smallsat-institute/sst-soa/deorbit-systems",
  "edition": "2026",
  "scrape_date": "2026-05-19",
  "columns": ["Manufacturer", "Host Spacecraft", "Device Mass (kg)", "Drag Area (m²)", "Launch Year", "TRL"],
  "_notes": ["Note that all data is documented as provided in the references..."],
  "data": [
    {
      "Manufacturer": "CU Aerospace",
      "Host Spacecraft": "TechEdSat-3",
      "Device Mass (kg)": "0.06",
      "Drag Area (m²)": "1.0",
      "Launch Year": "2012",
      "TRL": "F"
    }
  ]
}
```

### Subgroup-split file

When a table has named internal sections (e.g., "Integrated Propulsion Systems" / "Thruster Heads"), each section becomes a separate file. A `subgroup` field is added:

```json
{
  "table_id": "4-7",
  "subgroup": "Integrated Propulsion Systems",
  "title": "Electrothermal Electric Propulsion",
  ...
}
```

Files sharing the same `table_id` belong to the same original NASA table.

### Field reference

| Field | Type | Description |
|-------|------|-------------|
| `table_id` | string | NASA table number, e.g. `"4-7"` |
| `subgroup` | string | Section name within the table (only present for split files) |
| `title` | string | Table title as shown in the report (text after the colon) |
| `chapter_num` | integer | Chapter number (1–13) |
| `chapter_title` | string | Full chapter name |
| `source_url` | string | URL of the NASA chapter page |
| `edition` | string | Report edition year, `"2026"` |
| `scrape_date` | string | ISO 8601 date the data was scraped |
| `type` | string | Table classification: `"products"`, `"specifications"`, or `"reference"` — see below |
| `columns` | array of strings | Column headers exactly as shown in the report, including units |
| `_notes` | array of strings | Footnotes from the bottom of the table (empty array if none) |
| `data` | array of objects | Row data; keys match `columns` exactly |

### Missing values

NASA uses an en-dash (`–`) to indicate data that is not available or not applicable. This convention is preserved in all JSON files. Missing values are stored as `"–"`, not as `null` or `""`.

### Table types

Every JSON file includes a `type` field classifying the table's content:

| Value | Description | Example |
|-------|-------------|---------|
| `"products"` | Rows are specific commercial or government products/services with technical specifications | Table 3-5 (battery product table), Table 5-3 (reaction wheels) |
| `"specifications"` | General parameters, design guidelines, standards, or comparison data — not specific products | Table 3-6 (battery vs. supercapacitor), Table 6-1 (CubeSat dimensions) |
| `"reference"` | Overview, summary, classification, mission list, or contact information | Table 4-1 (propulsion technology summary), Table 2-9 (contact info) |

This field lets you quickly filter tables when searching across chapters:

```python
# Find all product tables across all chapters
for json_file in sorted(Path(".").glob("*/table_*.json")):
    with open(json_file) as f:
        t = json.load(f)
    if t["type"] == "products":
        print(f"Ch{t['chapter_num']} Table {t['table_id']}: {t['title']} ({len(t['data'])} rows)")
```

---

## Subgroup Files (Chapters 4 and 11)

Several chapters contain tables with named internal subgroups that divide products into categories. These are stored as separate files so each file contains a coherent set of rows.

**Chapter 4 (Propulsion)** — most propulsion product tables split into:
- `_integrated_systems` — complete propulsion systems (thruster + propellant + feed system in one unit)
- `_thruster_heads` — thruster components sold separately (require an external propellant feed)

**Chapter 11 (Ground Data Systems)** — Tables 11-3 and 11-5 split by communication direction:
- Table 11-3: terrestrial link data transport vs. spacecraft navigation tracking
- Table 11-5: forward (command) vs. return (telemetry) communications

---

## Known Limitations

- **NASA duplicate table numbers (2026 edition):** NASA's 2026 pages reuse some
  table numbers for two unrelated tables. `Table 4-1` labels both *Summary of
  Propulsion Technologies Surveyed* and *Hydrazine Chemical Propulsion* (the
  chapter prose references a "Table 4-2" for hydrazine, but no table is actually
  labeled 4-2); `Table 6-7` labels both *Robotic Arms for Small Spacecraft* and
  *Polylactic Acid Filaments*. The data is preserved exactly as NASA published
  it — files share the NASA `table_id` but are kept as separate JSON files
  distinguished by title. The `type` field reflects the legitimately numbered
  table for that id.
- **2026 restructuring:** NASA reorganized several chapters relative to 2024.
  Avionics (Ch 8) expanded from 2 to 6 tables (adding AI applications, flight
  software, and operating systems); Integration, Launch & Deployment (Ch 10)
  expanded from 1 to 4 tables; and chapters 3, 4, and 6 dropped or renumbered
  tables. The fully scraped 2024 edition remains available on the
  [`master-2024-report`](../../tree/master-2024-report) branch.
- Data accuracy depends on NASA's source pages. The report notes that "performance data may be speculative" and relies on manufacturer datasheets.
- Some tables contain merged cells (rowspan) that the scraper expands by repeating the spanning value across all affected rows.

---

## How to Use

### Python

```python
import json
from pathlib import Path

# Load a single table
with open("04-in-space-propulsion/table_4-7_electrothermal_integrated_systems.json") as f:
    table = json.load(f)

print(table["title"])          # "Electrothermal Electric Propulsion"
print(table["subgroup"])       # "Integrated Propulsion Systems"
print(table["columns"])        # ["Manufacturer", "Product", "Propellant", ...]

for row in table["data"]:
    print(row["Manufacturer"], row.get("Thrust [mN]", "–"))
```

### Load all tables from a chapter

```python
import json
from pathlib import Path

chapter_dir = Path("04-in-space-propulsion")
tables = []
for json_file in sorted(chapter_dir.glob("table_*.json")):
    with open(json_file) as f:
        tables.append(json.load(f))

print(f"Loaded {len(tables)} tables from Chapter 4")
```

### Find all product tables across all chapters

```python
import json
from pathlib import Path

for json_file in sorted(Path(".").glob("*/table_*.json")):
    with open(json_file) as f:
        t = json.load(f)
    # Each file is self-describing — table_id, chapter, columns, data are always present
    print(f"Ch{t['chapter_num']} Table {t['table_id']}: {t['title']} ({len(t['data'])} rows)")
```

---

## Re-running the Scraper

To re-scrape the data from NASA's website:

```bash
pip install -r scraper/requirements.txt
python scraper/scrape.py
```

Options:
```
--chapters 2,3,4   Scrape only specific chapters (default: all)
--cache            Cache downloaded HTML in scraper/.cache/ for faster re-runs
--output-dir .     Root directory for output (default: repo root)
```

The scraper uses a 1-second delay between chapter requests to avoid overloading NASA's servers.

### Updating to a new edition

NASA publishes a new edition annually. To regenerate this dataset for a newer
edition, bump the `EDITION` constant in [`scraper/config.py`](scraper/config.py)
(and the `title` of any renamed chapter), then re-run the scraper. Each run
rewrites every table and **prunes stale files** — table JSONs no longer present
in the new edition are removed automatically, so each scrape yields a clean
single-edition snapshot. Archive the outgoing edition to its own branch (as the
2024 edition is, on `master-2024-report`) before merging the new one.

---

## License

- **Data**: NASA content is a work of the U.S. government and is in the public domain within the United States. See [nasa.gov/about/contact/copyright](https://www.nasa.gov/about/contact/copyright/).
- **Scraper code** (`scraper/`): MIT License.

---

## About

Scraped and structured by [Harald Luiks](https://github.com/HaralDev). The goal was simply to make this useful dataset easier to work with — no original research, just extraction and formatting of NASA's publicly available report.
