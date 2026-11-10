"""Merge verified shloka patches into data/epic-sources/{ramayana,mahabharata}.json."""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "data" / "epic-sources"
PAIRS = {
    "ramayana.json": ["ram-a.json", "ram-b.json"],
    "mahabharata.json": ["mbh.json"],
}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    for main_name, patch_names in PAIRS.items():
        path = SRC / main_name
        data = load(path)
        items = data["entries"]
        by_id = {i["id"]: i for i in items}
        for pn in patch_names:
            for pid, shloka in load(SRC / "patches" / pn)["entries"].items():
                if pid in by_id and shloka:
                    by_id[pid]["shloka"] = shloka
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(main_name, sum(1 for i in items if i.get("shloka")), "/", len(items))


if __name__ == "__main__":
    main()
