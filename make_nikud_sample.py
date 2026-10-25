# Build the pointed-Hebrew sample from Daat Siddur Ashkenaz (Public Domain, via the Sefaria API v3 JSON files).
# Source: Sefaria API v3 (/api/v3/texts/<ref>), version "Daat Siddur Ashkenaz". Refs: "Siddur Ashkenaz, Shabbat, Havdalah";
#   "Siddur Ashkenaz, Berachot, Birkat Hanehenin, Eating, Barachot Rishonot"; "Siddur Ashkenaz, Berachot, Birkhot Hamitzvot";
#   "Siddur Ashkenaz, Festivals, Chanukah, Service for Lighting Chanukah Candles, Blessings on Chanukah Candles".
#   The output files are included in the repo, so readers do not need to fetch these.
# Usage: python3 -I make_nikud_sample.py <src dir with Sefaria JSON> <out dir>
# Writes nikud_pointed.txt (vowels kept, cantillation U+0591-05AF removed) and nikud_plain.txt (all marks removed).
import json, re, sys, pathlib
FILES = ["Havdalah.json", "Barachot_Rishonot.json", "Birkhot_Hamitzvot.json", "Chanukah_Blessings.json"]
def flat(x):
    if isinstance(x, str): yield x
    elif isinstance(x, list):
        for y in x: yield from flat(y)
src, out = map(pathlib.Path, sys.argv[1:3])
lines = []
for f in FILES:
    d = json.load(open(src / f, encoding="utf-8"))
    v = next(v for v in d["versions"] if v.get("versionTitle") == "Daat Siddur Ashkenaz")
    for s in flat(v["text"]):
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"[\u0591-\u05AF]", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s: lines.append(s)
pointed = "\n".join(lines) + "\n"
plain = re.sub(r"[\u05B0-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]", "", pointed)
(out / "nikud_pointed.txt").write_text(pointed, encoding="utf-8")
(out / "nikud_plain.txt").write_text(plain, encoding="utf-8")
print(len(lines), "lines,", len(plain.split()), "words")
