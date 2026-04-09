from dataclasses import dataclass, field


@dataclass
class ChapterConfig:
    chapter_num: int
    slug: str
    title: str
    url: str
    output_folder: str


CHAPTERS: list[ChapterConfig] = [
    ChapterConfig(
        chapter_num=1,
        slug="introduction",
        title="Introduction",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/introduction",
        output_folder="01-introduction",
    ),
    ChapterConfig(
        chapter_num=2,
        slug="platforms",
        title="Complete Spacecraft Platforms",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/platforms",
        output_folder="02-platforms",
    ),
    ChapterConfig(
        chapter_num=3,
        slug="power-subsystems",
        title="Power Subsystems",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems",
        output_folder="03-power-subsystems",
    ),
    ChapterConfig(
        chapter_num=4,
        slug="in-space_propulsion",
        title="In-Space Propulsion",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion",
        output_folder="04-in-space-propulsion",
    ),
    ChapterConfig(
        chapter_num=5,
        slug="guidance-navigation-and-control",
        title="Guidance, Navigation, and Control",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control",
        output_folder="05-guidance-navigation-and-control",
    ),
    ChapterConfig(
        chapter_num=6,
        slug="structures-materials-and-mechanisms",
        title="Structures, Materials, and Mechanisms",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/structures-materials-and-mechanisms",
        output_folder="06-structures-materials-and-mechanisms",
    ),
    ChapterConfig(
        chapter_num=7,
        slug="thermal-control",
        title="Thermal Control",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control",
        output_folder="07-thermal-control",
    ),
    ChapterConfig(
        chapter_num=8,
        slug="small-spacecraft-avionics",
        title="Small Spacecraft Avionics",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/small-spacecraft-avionics",
        output_folder="08-small-spacecraft-avionics",
    ),
    ChapterConfig(
        chapter_num=9,
        slug="soa-communications",
        title="Communications",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/soa-communications",
        output_folder="09-communications",
    ),
    ChapterConfig(
        chapter_num=10,
        slug="integration-launch-and-deployment",
        title="Integration, Launch, and Deployment",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/integration-launch-and-deployment",
        output_folder="10-integration-launch-and-deployment",
    ),
    ChapterConfig(
        chapter_num=11,
        slug="ground-data-systems-and-mission-operations",
        title="Ground Data Systems and Mission Operations",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/ground-data-systems-and-mission-operations",
        output_folder="11-ground-data-systems-and-mission-operations",
    ),
    ChapterConfig(
        chapter_num=12,
        slug="identification-and-tracking-systems",
        title="Identification and Tracking Systems",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/identification-and-tracking-systems",
        output_folder="12-identification-and-tracking-systems",
    ),
    ChapterConfig(
        chapter_num=13,
        slug="deorbit-systems",
        title="Deorbit Systems",
        url="https://www.nasa.gov/smallsat-institute/sst-soa/deorbit-systems",
        output_folder="13-deorbit-systems",
    ),
]
