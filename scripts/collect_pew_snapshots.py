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
    }


def main():
    out = {
        "generated_from": "manual verified extraction, single cited Pew report",
        "series": build_snapshots(),
    }
    path = Path("data/pew-snapshots.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Generated: {path.resolve()}")


if __name__ == "__main__":
    main()
