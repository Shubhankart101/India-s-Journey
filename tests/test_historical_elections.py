import unittest
import zipfile
from io import BytesIO
from xml.etree import ElementTree

from scripts.collect_historical_elections import parse_historical_workbook, read_xlsx_rows


def make_xlsx(rows, additional_sheets=None):
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    all_sheets = [rows, *(additional_sheets or [])]
    content = BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        workbook = ElementTree.Element(f"{{{main_ns}}}workbook")
        sheets = ElementTree.SubElement(workbook, f"{{{main_ns}}}sheets")
        relationships = ElementTree.Element(f"{{{package_rel_ns}}}Relationships")
        for index in range(len(all_sheets)):
            ElementTree.SubElement(sheets, f"{{{main_ns}}}sheet", {
                "name": f"Sheet{index + 1}",
                "sheetId": str(index + 1),
                f"{{{rel_ns}}}id": f"rId{index + 1}",
            })
            ElementTree.SubElement(relationships, f"{{{package_rel_ns}}}Relationship", {
                "Id": f"rId{index + 1}",
                "Type": "worksheet",
                "Target": f"/xl/worksheets/sheet{index + 1}.xml",
            })
        archive.writestr("xl/workbook.xml", ElementTree.tostring(workbook))
        archive.writestr("xl/_rels/workbook.xml.rels", ElementTree.tostring(relationships))
        for sheet_index, sheet_rows in enumerate(all_sheets, start=1):
            worksheet = ElementTree.Element(f"{{{main_ns}}}worksheet")
            sheet_data = ElementTree.SubElement(worksheet, f"{{{main_ns}}}sheetData")
            for row_index, values in enumerate(sheet_rows, start=1):
                row = ElementTree.SubElement(sheet_data, f"{{{main_ns}}}row", {"r": str(row_index)})
                for column_index, value in enumerate(values):
                    column = ""
                    number = column_index + 1
                    while number:
                        number, remainder = divmod(number - 1, 26)
                        column = chr(65 + remainder) + column
                    cell = ElementTree.SubElement(row, f"{{{main_ns}}}c", {"r": f"{column}{row_index}"})
                    if isinstance(value, (int, float)):
                        ElementTree.SubElement(cell, f"{{{main_ns}}}v").text = str(value)
                    else:
                        cell.set("t", "inlineStr")
                        inline = ElementTree.SubElement(cell, f"{{{main_ns}}}is")
                        ElementTree.SubElement(inline, f"{{{main_ns}}}t").text = value
            archive.writestr(
                f"xl/worksheets/sheet{sheet_index}.xml",
                ElementTree.tostring(worksheet),
            )
    return content.getvalue()


class HistoricalElectionTests(unittest.TestCase):
    def test_reads_inline_and_numeric_xlsx_cells(self):
        workbook = make_xlsx([["Election", 2023], ["State", "Karnataka"]])
        self.assertEqual(read_xlsx_rows(workbook), [["Election", "2023"], ["State", "Karnataka"]])

    def test_finds_detailed_results_beyond_the_first_worksheet(self):
        workbook = make_xlsx(
            [["Election summary"], ["Karnataka"]],
            [[
                ["State/UT Name", "AC No.", "AC Name", "Candidate Name", "Party", "Total Votes"],
                ["Karnataka", "1", "NIPPANI", "Candidate A", "Party A", 100],
            ]],
        )
        results = parse_historical_workbook(
            workbook,
            "Karnataka Assembly 2023",
            "https://old.eci.gov.in/files/file/15163-karnataka-2023/",
            "2023",
        )
        self.assertEqual(results[0]["constituency"], "NIPPANI")

    def test_parses_candidate_results_and_preserves_official_source(self):
        workbook = make_xlsx([
            ["State/UT Name", "AC No.", "AC Name", "Candidate Name", "Party", "Total Votes", "% of Votes Polled", "Total Electors"],
            ["Karnataka", "1", "NIPPANI", "Candidate A", "Party A", 51000, 54.2, 180000],
            ["Karnataka", "1", "NIPPANI", "Candidate B", "Party B", 43000, 45.8, 180000],
        ])
        source = "https://old.eci.gov.in/files/file/15163-karnataka-2023/"
        results = parse_historical_workbook(workbook, "2023", source, "2023")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["year"], 2023)
        self.assertEqual(results[0]["election_type"], "State Assembly")
        self.assertEqual(results[0]["constituency"], "NIPPANI")
        self.assertEqual(results[0]["votes"], 51000)
        self.assertEqual(results[0]["vote_share_percent"], 54.2)
        self.assertEqual(results[0]["electors"], 180000)
        self.assertEqual(results[0]["source"], source)

    def test_identifies_parliamentary_general_election_reports(self):
        workbook = make_xlsx([
            ["State/UT Name", "PC No.", "PC Name", "Candidate Name", "Party", "Total", "% Votes Polled"],
            ["Assam", "1", "KARIMGANJ", "Candidate A", "Party A", 3000, 51.5],
        ])
        results = parse_historical_workbook(
            workbook,
            "2019",
            "https://old.eci.gov.in/files/file/2019-lok-sabha/",
            "2019",
        )
        self.assertEqual(results[0]["election_type"], "Lok Sabha")
        self.assertEqual(results[0]["vote_share_percent"], 51.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
