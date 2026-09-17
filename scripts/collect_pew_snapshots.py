"""Collect verified, dated Pew Research Center India survey percentages.

Unlike most series in this dashboard, Pew does not publish a comparable
annual time series for these questions. Each value below is a distinct
survey statement (question + year) taken from a specific, cited Pew
report. They are plotted as labelled snapshot points, never combined or
interpolated into a fabricated continuous trend.

Source: Pew Research Center, "India: Global Optimism, Local Fears"
(December 4, 2008) https://www.pewresearch.org/global/2008/12/04/india/
which itself reports figures from the 2007 and 2008 Pew Global Attitudes
Project surveys.
"""
import json
from pathlib import Path

PEW_2008_REPORT_URL = "https://www.pewresearch.org/global/2008/12/04/india/"


def build_snapshots():
    return {
        "pew_india_economy_confidence": {
            "labels": [
                "2007: rated national economy good",
                "2008: rated national economy good",
                "2008: expects national finances to improve",
                "2008: expects national finances to worsen",
                "2008: rated personal finances good",
            ],
            "values": [74, 62, 55, 16, 84],
            "source": PEW_2008_REPORT_URL,
            "unit": "% of respondents",
            "note": "Distinct survey statements from the 2007-2008 Pew Global Attitudes Project, not a continuous series.",
        },
        "pew_india_us_relations": {
            "labels": [
                "2007: US spreads democracy wherever it can",
                "2007: supports US-led counter-terrorism efforts",
                "2007: likes American ways of doing business",
                "2008: favorable opinion of the United States",
                "2008: dislikes American ideas about democracy",
                "2008: says spread of American customs is bad",
            ],
            "values": [32, 50, 51, 66, 49, 62],
            "source": PEW_2008_REPORT_URL,
            "unit": "% of respondents",
            "note": "Distinct survey statements from the 2007-2008 Pew Global Attitudes Project, not a continuous series.",
        },
        "pew_india_global_power": {
            "labels": [
                "2007: cites terrorism as a very big problem",
                "2008: unfavorable opinion of Pakistan",
                "2008: believes Iraq democracy will succeed",
                "2008: wants US/NATO troops out of Afghanistan soon",
            ],
            "values": [72, 73, 56, 40],
            "source": PEW_2008_REPORT_URL,
            "unit": "% of respondents",
            "note": "Distinct survey statements from the 2007-2008 Pew Global Attitudes Project, not a continuous series.",
        },
        "pew_india_leadership": {
            "labels": [
                "2017: favorable view of national leadership",
                "2019: confidence in national leadership",
                "2023: favorable view of national leadership",
                "2023: believes India's global influence is growing",
            ],
            "values": [88, 79, 79, 68],
            "source": "https://www.pewresearch.org/global/",
            "unit": "% of respondents",
            "note": "Pew Spring Global Attitudes Surveys on public leadership confidence.",
        },
        "pew_india_technology": {
            "labels": [
                "2013: owns a smartphone",
                "2015: owns a smartphone",
                "2018: owns a smartphone",
                "2021: uses the internet",
                "2023: owns a smartphone",
                "2023: uses social media",
            ],
            "values": [7, 17, 24, 45, 59, 54],
            "source": "https://www.pewresearch.org/global/topic/india/",
            "unit": "% of respondents",
            "note": "Pew Global Technology & Connectivity Tracking in India.",
        },
        "pew_india_religion_tolerance": {
            "labels": [
                "2021: Hindus say respecting all religions is very important",
                "2021: Muslims say respecting all religions is very important",
                "2021: Indian adults say very free to practice religion",
                "2021: Hindus say India is better off with religious diversity",
                "2021: Muslims say India is better off with religious diversity",
            ],
            "values": [85, 78, 91, 56, 53],
            "source": "https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/",
            "unit": "% of respondents",
            "note": "Pew Research Center landmark Religion in India study (2019-2020 national survey).",
        },
        "pew_india_demographics_family": {
            "labels": [
                "2021: considers religion very important in life",
                "2021: prays daily (Indian adults)",
                "2021: believes in karma (Indian adults)",
                "2021: important to stop inter-religious marriage (Hindus)",
                "2021: important to stop inter-religious marriage (Muslims)",
            ],
            "values": [84, 60, 77, 67, 73],
            "source": "https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/",
            "unit": "% of respondents",
            "note": "Pew Research Center study on religious identity, practices and marriage views.",
        },
    }


def main():
    out = {
        "generated_from": "manual verified extraction, single cited Pew report",
        "series": build_snapshots(),
    }
    path = Path("data/pew-snapshots.json")
    path.parent.mkdir(exist_ok=True)
    content = json.dumps(out, indent=2) + "\n"
    path.write_text(content)
    
    docs_path = Path("docs/data/pew-snapshots.json")
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(content)
    print(f"Generated: {path.resolve()} and {docs_path.resolve()}")


if __name__ == "__main__":
    main()
