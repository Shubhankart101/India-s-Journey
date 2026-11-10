"""Build the sourced voter-roll explainer data for static and React views."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS_ELECTORS = "https://www.eci.gov.in/EBooks/atlas-2024/files/basic-html/page136.html"
ATLAS_TURNOUT = "https://www.eci.gov.in/EBooks/atlas-2024/files/basic-html/page90.html"
CENSUS_POPULATION = "https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab8.7.pdf"
WORLD_BANK_POPULATION = "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL?format=json"
VOTING_AGE = "https://www.legislative.gov.in/static/uploads/2025/07/8446eabf82b28598535e8c5f1ef65508.pdf"
SSR_2024 = "https://pib.gov.in/PressReleaseshare.aspx?PRID=2005189"
RULES = "https://www.eci.gov.in/eci/public/api/document?id=17496"
FORMS = "https://voters.eci.gov.in/home/forms"
SIR_BIHAR = "https://www.eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzIC5IR1A3V88Anuk8RlyPGe5wAx9KElz%2FMrntZbUSdw4Bx5SvVNRoI9UBA77hlBw0pIBUAIIvl27RVB1LxrL5Mw%3D%3D"
SIR_PHASE_II = "https://www.eci.gov.in/eci/public/api/document?id=17091"
SIR_PHASE_III = "https://www.eci.gov.in/eci/public/api/document?id=17344"
SIR_PHASE_III_START = "https://www.eci.gov.in/eci/public/api/document?id=17360"
DELETION_GUIDANCE = "https://old.eci.gov.in/files/file/15225-deletion-of-the-names-of-electors-from-the-electoral-roll-in-case-of-shifting-demographic-similar-entries-dses-and-death-regarding/"
SSR_DELETION_CHECKS = "https://www.eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzPKLkuiExxOKadAHYzWQYgrziMWVM9RdSa49qKKjiLLA79f6foe5mX9KNyNO9oZG7PCB8LrBlJ%2FOvwekvS9fQ6A%3D%3D"

# Electors: ECI Atlas 2024 Annexure I, p. 112. Turnout: ECI Atlas 2024, table T28.1.
ELECTION_ROWS = [
    ("1951–52", 173_213_635, 45.67, 1951, 361_088_000),
    ("1957", 193_652_179, 47.74, 1961, 439_235_000),
    ("1962", 216_361_569, 55.42, 1961, 439_235_000),
    ("1967", 250_207_401, 61.04, 1971, 548_160_000),
    ("1971", 274_189_132, 55.27, 1971, 548_160_000),
    ("1977", 321_174_327, 60.49, 1981, 683_329_000),
    ("1980", 356_205_329, 56.92, 1981, 683_329_000),
    ("1984–85", 400_375_333, 64.01, 1981, 683_329_000),
    ("1989", 498_906_129, 61.95, 1991, 846_421_000),
    ("1991–92", 511_533_598, 55.88, 1991, 846_421_000),
    ("1996", 592_572_288, 57.94, 2001, 1_028_737_000),
    ("1998", 605_880_192, 61.97, 2001, 1_028_737_000),
    ("1999", 619_536_847, 59.99, 2001, 1_028_737_000),
    ("2004", 671_487_930, 58.07, 2001, 1_028_737_000),
    ("2009", 716_985_101, 58.21, 2011, 1_210_855_000),
    ("2014", 834_082_814, 66.44, 2011, 1_210_855_000),
    ("2019", 911_950_734, 67.40, 2011, 1_210_855_000),
    ("2024", 979_751_847, 66.10, 2023, 1_438_069_596),
]

PHASE_II_STATES = [
    "Andaman & Nicobar Islands", "Chhattisgarh", "Goa", "Gujarat", "Kerala", "Lakshadweep",
    "Madhya Pradesh", "Puducherry", "Rajasthan", "Tamil Nadu", "Uttar Pradesh", "West Bengal",
]
PHASE_III_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Haryana", "Punjab", "Telangana", "Karnataka", "Maharashtra",
    "Jharkhand", "Odisha", "Uttarakhand", "Meghalaya", "Manipur", "Mizoram", "Nagaland", "Sikkim", "Tripura",
    "Dadra & Nagar Haveli and Daman & Diu", "Chandigarh", "Delhi",
]
ALL_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman & Nicobar Islands", "Chandigarh",
    "Dadra & Nagar Haveli and Daman & Diu", "Delhi", "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


def build_data() -> dict:
    elections = []
    for label, electors, turnout, population_year, population in ELECTION_ROWS:
        population_source = WORLD_BANK_POPULATION if population_year == 2023 else CENSUS_POPULATION
        elections.append({
            "label": label,
            "year": int(label[:4]),
            "electors": electors,
            "turnout_percent": turnout,
            "population": population,
            "population_year": population_year,
            "sources": {
                "electors": ATLAS_ELECTORS,
                "turnout": ATLAS_TURNOUT,
                "population": population_source,
            },
        })

    phase_by_state = {"Bihar": {"phase": 1, "status": "Completed; final roll published 30 September 2025", "source": SIR_BIHAR}}
    phase_by_state.update({name: {"phase": 2, "status": "Phase II ordered 4 November 2025", "source": SIR_PHASE_II} for name in PHASE_II_STATES})
    phase_by_state.update({name: {"phase": 3, "status": "Phase III ordered 14 May 2026", "source": SIR_PHASE_III} for name in PHASE_III_STATES})
    phase_by_state.update({name: {"phase": 3, "status": "Phase III enumeration began 30 May 2026", "source": SIR_PHASE_III_START} for name in ["Odisha", "Mizoram", "Sikkim", "Manipur"]})
    sir_states = []
    for name in ALL_STATES:
        phase = phase_by_state.get(name, {})
        row = {"state": name, "phase": phase.get("phase"), "status": phase.get("status", "No phase status or comparable roll totals in this source set"), "source": phase.get("source", SIR_PHASE_III)}
        if name == "Bihar":
            row.update({"before": 78_900_000, "draft": 72_400_000, "final": 74_200_000, "rounded": True, "source": SIR_BIHAR})
        sir_states.append(row)

    qualifiers = [
        {"id": "jan", "title": "1 January", "label": "Qualifying date", "detail": "An elector who is 18 on this date may qualify for enrolment in the current revision. The published 2024 summary roll used 1 January 2024.", "source": SSR_2024},
        {"id": "apr", "title": "1 April", "label": "Quarterly date", "detail": "Applications may also be made in advance for the next qualifying date; the ERO considers them in the relevant quarter.", "source": RULES},
        {"id": "jul", "title": "1 July", "label": "Quarterly date", "detail": "A third qualifying date provides another route for people who turn 18 later in the year.", "source": RULES},
        {"id": "oct", "title": "1 October", "label": "Quarterly date", "detail": "The fourth qualifying date completes the annual cycle; eligibility is assessed against the chosen date.", "source": SSR_2024},
        {"id": "draft", "title": "Draft roll", "label": "Public inspection", "detail": "The draft roll is opened for inspection. Check your entry and the polling part before the claims-and-objections period closes.", "source": RULES},
        {"id": "claims", "title": "Claims & objections", "label": "Forms 6, 7 and 8", "detail": "New enrolment, objections and corrections are submitted to the Electoral Registration Officer; the claims and objections are publicly listed under the rules.", "source": RULES},
        {"id": "final", "title": "Final roll", "label": "Updated list", "detail": "After claims and objections are disposed of, the revised roll is published. Continuous updation remains available between revisions, subject to election-period cut-offs.", "source": RULES},
    ]

    scenarios = [
        {"id": "turned-18", "title": "I turned 18", "form": "Form 6", "action": "Apply for inclusion as a new elector. If a qualifying date is upcoming, an advance application can be made for that quarter.", "steps": ["Submit Form 6 online or through your BLO/ERO.", "The registration office checks the application and may arrange local verification.", "Track the application; the ERO decides whether to add the entry to the roll."], "source": FORMS},
        {"id": "moved", "title": "I moved house", "form": "Form 8", "action": "Request shifting of your entry to your current ordinary residence, within or between constituencies.", "steps": ["Submit Form 8 with your new residence details.", "The ERO verifies the old entry and the new address.", "Check the updated roll and application status online."], "source": FORMS},
        {"id": "wrongly-deleted", "title": "My name was wrongly deleted", "form": "Form 6", "action": "Apply again for inclusion and give the details needed to identify the earlier entry; use the portal's appeal/status facilities if an order has already been issued.", "steps": ["File Form 6 with the electoral registration office.", "Ask your BLO or ERO for help locating the deletion record.", "Track the claim and follow any notice or appeal route shown by the ECI portal."], "source": FORMS},
        {"id": "nri", "title": "I live abroad", "form": "Form 6A", "action": "An Indian citizen who has not acquired another citizenship can apply as an overseas elector at the Indian address in the passport.", "steps": ["Submit Form 6A on the ECI service portal or to the ERO.", "The registration office verifies the passport and ordinary-residence details.", "Track the application with the portal or contact the ERO."], "source": FORMS},
        {"id": "correction", "title": "My details are wrong", "form": "Form 8", "action": "Request correction of particulars, replacement EPIC, or marking of disability in the electoral roll.", "steps": ["Submit Form 8 with the entry to be corrected.", "Attach relevant supporting details requested by the form.", "Track the application and check the published roll for the corrected entry."], "source": FORMS},
        {"id": "remove", "title": "Remove an ineligible or duplicate entry", "form": "Form 7", "action": "Use Form 7 to request deletion of your own entry or to object to an entry, stating the applicable ground.", "steps": ["Submit Form 7 to the ERO, online or through the local election office.", "The registration office checks the stated ground and follows applicable verification and notice procedures.", "Track the claim and respond to any notice from the ERO."], "source": FORMS},
    ]

    return {
        "meta": {
            "title": "India's electoral roll: SSR and SIR",
            "generated_from": "ECI, PIB, Census of India and World Bank official sources",
        },
        "sources": {
            "electors": {"label": "ECI Atlas 2024, Annexure I", "url": ATLAS_ELECTORS},
            "turnout": {"label": "ECI Atlas 2024, table T28.1", "url": ATLAS_TURNOUT},
            "population_census": {"label": "Economic Survey, Table 8.7 (Census of India totals)", "url": CENSUS_POPULATION},
            "population_world_bank": {"label": "World Bank, India population total (SP.POP.TOTL)", "url": WORLD_BANK_POPULATION},
            "voting_age": {"label": "Constitution (Sixty-first Amendment) Act, 1988", "url": VOTING_AGE},
            "ssr_2024": {"label": "ECI / PIB, Special Summary Revision 2024", "url": SSR_2024},
            "registration_rules": {"label": "Registration of Electors Rules, 1960", "url": RULES},
            "forms": {"label": "ECI Voter Service Portal forms", "url": FORMS},
            "sir_bihar": {"label": "ECI Bihar SIR final press note, 30 September 2025", "url": SIR_BIHAR},
            "sir_phase_ii": {"label": "ECI SIR Phase II press note, 4 November 2025", "url": SIR_PHASE_II},
            "sir_phase_iii": {"label": "ECI SIR Phase III press note, 14 May 2026", "url": SIR_PHASE_III},
            "sir_phase_iii_start": {"label": "ECI Phase III enumeration start note, 31 May 2026", "url": SIR_PHASE_III_START},
            "deletion_guidance": {"label": "ECI instructions on deletions, 11 August 2023", "url": DELETION_GUIDANCE},
            "deletion_thresholds": {"label": "ECI SSR deletion cross-check instructions", "url": SSR_DELETION_CHECKS},
        },
        "figures": {
            "elections": {
                "title": "From 17 crore to nearly 98 crore electors",
                "source": [ATLAS_ELECTORS, ATLAS_TURNOUT, CENSUS_POPULATION, WORLD_BANK_POPULATION, VOTING_AGE],
                "population_note": "Population uses the nearest Census year through 2011; the 2024 election is paired with the latest cited World Bank estimate (2023).",
                "turnout_note": "ECI turnout percentages for 2024 exclude Surat, where the election was uncontested.",
            },
            "sir": {"title": "SIR state by state", "source": [SIR_BIHAR, SIR_PHASE_II, SIR_PHASE_III, SIR_PHASE_III_START]},
            "calendar": {"title": "SSR every year", "source": [RULES, SSR_2024]},
            "deletions": {"title": "What gets removed", "source": [SSR_2024, DELETION_GUIDANCE, SSR_DELETION_CHECKS]},
            "forms": {"title": "Forms 6, 7, 8 and 6A", "source": [FORMS, RULES, SIR_PHASE_II]},
        },
        "elections": elections,
        "sir": {
            "states": sir_states,
            "phases": [
                {"phase": 1, "scope": ["Bihar"], "status": "Completed; ECI published the final roll on 30 September 2025.", "source": SIR_BIHAR},
                {"phase": 2, "scope": PHASE_II_STATES, "status": "ECI ordered SIR in 9 States and 3 UTs on 4 November 2025.", "source": SIR_PHASE_II},
                {"phase": 3, "scope": PHASE_III_STATES, "status": "ECI ordered Phase III in 16 States and 3 UTs on 14 May 2026; four states began enumeration on 30 May 2026.", "source": SIR_PHASE_III},
            ],
            "note": "Only Bihar has comparable before, draft and final totals in this dataset. Grey states have no verified before/final pair here; that does not mean they were not revised.",
        },
        "calendar": qualifiers,
        "deletions": {
            "total_reported": 16_576_654,
            "reasons": [
                {"label": "Deceased electors", "value": 6_782_642, "source": SSR_2024},
                {"label": "Permanently shifted / absent", "value": 7_511_128, "source": SSR_2024},
                {"label": "Duplicate entries", "value": 2_205_685, "source": SSR_2024},
            ],
            "ratios": [
                {"label": "Electors per 100 people", "before": 65.99, "after": 66.76, "source": SSR_2024},
                {"label": "Women electors per 1,000 men", "before": 943, "after": 948, "source": SSR_2024},
            ],
            "safeguards": [
                {"title": "Field checks", "detail": "The ECI's deletion instructions require verification of the stated ground; a field verification report is part of the prescribed process.", "source": DELETION_GUIDANCE},
                {"title": "Notice and hearing", "detail": "For specified proposed deletions, the elector must receive notice and a reasonable opportunity to be heard before the entry is removed.", "source": DELETION_GUIDANCE},
                {"title": "Escalation for unusual batches", "detail": "ECI instructions require personal ERO cross-checks when a polling station's deletions exceed 2% of its electors, or one objector files more than five cases.", "source": SSR_DELETION_CHECKS},
                {"title": "A public claims window", "detail": "Draft publication and claims/objections procedures create a route to challenge or correct an entry before the final roll is published.", "source": RULES},
            ],
            "note": "ECI/PIB reported 16,576,654 total deletions. The three published reason counts sum to 16,499,455, a difference of 77,199; the source does not assign that difference to a reason, so it is left unexplained here.",
        },
        "scenarios": scenarios,
    }


def main() -> None:
    payload = build_data()
    targets = [ROOT / "data" / "voter-roll.json",
               ROOT / "frontend" / "src" / "data" / "voter-roll.json", ROOT / "frontend" / "public" / "data" / "voter-roll.json"]
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded, encoding="utf-8")
    print(f"Wrote sourced voter-roll data ({len(payload['elections'])} elections, {len(payload['sir']['states'])} States/UTs) to {len(targets)} copies")


if __name__ == "__main__":
    main()