# Chapter 4 — In-Space Propulsion

**Source:** https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion  
**Edition:** 2024  
**Data scraped:** 2026-04-09

## Files in this folder

| File | NASA Table | Type | Subgroup |
|------|-----------|------|---------|
| table_4-1_summary_4_6_1_chemical_propulsion_technologies.json | Table 4-1: Summary of Propulsion Technologies Surveyed | reference | 4.6.1 CHEMICAL PROPULSION TECHNOLOGIES |
| table_4-1_summary_4_6_2_electric_propulsion_technologies.json | Table 4-1: Summary of Propulsion Technologies Surveyed | reference | 4.6.2 ELECTRIC PROPULSION TECHNOLOGIES |
| table_4-1_summary_4_6_3_propellantless_propulsion_technologies.json | Table 4-1: Summary of Propulsion Technologies Surveyed | reference | 4.6.3 PROPELLANTLESS PROPULSION TECHNOLOGIES |
| table_4-2_hydrazine_chemical_propulsion_integrated_systems.json | Table 4-2: Hydrazine Chemical Propulsion | products | Integrated Propulsion Systems |
| table_4-2_hydrazine_chemical_propulsion_thruster_heads.json | Table 4-2: Hydrazine Chemical Propulsion | products | Thruster |
| table_4-3_alt_monobiprop_integrated_systems.json | Table 4-3: Alternative Monopropellant and Bipropellant Propulsion | products | Integrated Propulsion Systems |
| table_4-3_alt_monobiprop_thruster_heads.json | Table 4-3: Alternative Monopropellant and Bipropellant Propulsion | products | Thruster Heads |
| table_4-4_hybrid_chemical.json | Table 4-4: Hybrid Chemical Propulsion | products | — |
| table_4-5_cold_gas_integrated_systems.json | Table 4-5: Cold Gas Propulsion | products | Integrated Propulsion Systems |
| table_4-5_cold_gas_thruster_heads.json | Table 4-5: Cold Gas Propulsion | products | Thruster Heads |
| table_4-6_solid_motor_integrated_systems.json | Table 4-6: Solid Motor Chemical Propulsion | products | Integrated Propulsion Systems |
| table_4-6_solid_motor_thruster_heads.json | Table 4-6: Solid Motor Chemical Propulsion | products | Thruster Heads |
| table_4-7_electrothermal_integrated_systems.json | Table 4-7: Electrothermal Electric Propulsion | products | Integrated Propulsion Systems |
| table_4-7_electrothermal_thruster_heads.json | Table 4-7: Electrothermal Electric Propulsion | products | Thruster Heads |
| table_4-8_electrospray_integrated_systems.json | Table 4-8: Electrospray Electric Propulsion | products | Integrated Propulsion Systems |
| table_4-9_gridded_ion_integrated_systems.json | Table 4-9: Gridded-Ion Electric Propulsion | products | Integrated Propulsion Systems |
| table_4-9_gridded_ion_thruster_heads.json | Table 4-9: Gridded-Ion Electric Propulsion | products | Thruster Heads |
| table_4-10_hall_effect.json | Table 4-10: Hall-Effect Electric Propulsion Thrusters | products | — |
| table_4-11_pulsed_plasma_integrated_systems.json | Table 4-11: Pulsed Plasma and Vacuum Arc Electric Propulsion | products | Integrated Propulsion Systems |
| table_4-12_ambipolar_integrated_systems.json | Table 4-12: Ambipolar Electric Propulsion | products | Integrated Propulsion Systems |
| table_4-13_propellantless.json | Table 4-13: Propellant-less Propulsion | products | — |

**Table types:**

- **products**: rows are specific commercial or government products/services with technical specs
- **reference**: overview, summary, or classification table

## Notes on table structure

- **Table 4-10**: The HTML source contained a "(cont.)" continuation section that has been merged into the relevant subgroup files.
- **Table 4-3**: The HTML source contained a "(cont.)" continuation section that has been merged into the relevant subgroup files.
- **Subgroup splits**: Some tables contain full-width row separators that divide data into named sections (e.g., "Integrated Propulsion Systems" / "Thruster Heads"). Each section is stored as a separate JSON file. Files sharing the same `table_id` prefix belong to the same original table.

## References

1. In-Space Chemical Propulsion (4.6.1)
2. In-Space Electric Propulsion (4.6.2)
3. In-Space Propellant-less Propulsion (4.6.3)
