# Chapter 11 — Ground Data Systems and Mission Operations

**Source:** https://www.nasa.gov/smallsat-institute/sst-soa/ground-data-systems-and-mission-operations  
**Edition:** 2026  
**Data scraped:** 2026-05-19

## Files in this folder

| File | NASA Table | Type | Subgroup |
|------|-----------|------|---------|
| table_11-1_primary_elements.json | Table 11-1: Primary Elements of a Ground System | reference | — |
| table_11-2_frequency_bands.json | Table 11-2: Frequency Bands | specifications | — |
| table_11-3_nsn_interfaces_and_capabilities_terrestrial_link_data_transport.json | Table 11-3: NSN Interfaces and Capabilities | specifications | Terrestrial Link Data Transport Capabilities |
| table_11-3_nsn_interfaces_and_capabilities_spacecraft_navigation_tracking.json | Table 11-3: NSN Interfaces and Capabilities | specifications | Spacecraft Navigation Tracking Capabilities |
| table_11-4_nsn_supported_radio_frequencies.json | Table 11-4: NSN Supported Radio Frequencies and Bandwidths | specifications | — |
| table_11-5_nsn_dte_capabilities_forward_command.json | Table 11-5: NSN Direct to Earth Command and Telemetry Capabilities per Frequency | specifications | Forward (Command) Communications |
| table_11-5_nsn_dte_capabilities_return_telemetry.json | Table 11-5: NSN Direct to Earth Command and Telemetry Capabilities per Frequency | specifications | Return (Telemetry) Communications |
| table_11-6_dsn_customers_and_services.json | Table 11-6: DSN Customers, Mission Characteristics, Frequencies, and Services | reference | — |
| table_11-7_atlas_federated_antenna_network.json | Table 11-7: ATLAS Federated Antenna Network | products | — |
| table_11-8_viasat_ground_stations.json | Table 11-8: Viasat Ground Stations | products | — |
| table_11-9_service_providers_space_relay.json | Table 11-9: Service Providers for Space Relay Networks | products | — |
| table_11-10_ground_system_components.json | Table 11-10: Ground System Components | products | — |
| table_11-11_software_for_ground_systems.json | Table 11-11: Software for Ground Systems | products | — |
| table_11-12_end_to_end_hardware_for_ground_systems.json | Table 11-12: End-to-End Hardware for Ground Systems | products | — |
| table_11-13_projected_performance_legs.json | Table 11-13: Projected Performance of LEGS Assets Pending Finalization | specifications | — |
| table_11-14_service_providers_dte_ground.json | Table 11-14: Service Providers for DTE Ground System Network | products | — |
| table_11-15_frequency_bands_infostellar.json | Table 11-15: Select Frequency Bands by InfoStellar | specifications | — |
| table_11-16_mission_ops_and_scheduling.json | Table 11-16: Mission Operations and Scheduling Software | products | — |

**Table types:**

- **products**: rows are specific commercial or government products/services with technical specs
- **specifications**: design parameters, standards, or comparison data (not specific products)
- **reference**: overview, summary, or classification table

## Notes on table structure

- **Subgroup splits**: Some tables contain full-width row separators that divide data into named sections (e.g., "Integrated Propulsion Systems" / "Thruster Heads"). Each section is stored as a separate JSON file. Files sharing the same `table_id` prefix belong to the same original table.
- **Table 11-17** (European Optical Nucleus Network OGS Key Parameters): This table is published as a PNG image on the NASA page and cannot be extracted as structured data. It is not included in this folder.

## References

1. Mission Integration – this includes development of service agreements, interfaces, documentation, support of reviews, etc.
2. Mission Planning and Scheduling – this includes performing link and loading analyses, supporting service requests, and generating and implementing operational schedules.
3. User Mission Data Transfer – this primarily includes spacecraft forward command and return telemetry data.
4. Position, Navigation and Timing (PNT) – this includes navigation.
