# Census, nikud cost and prefix test with the exact-pattern encoders.
# Usage: python3 -I analyze.py <dir with tokenizer files>
import sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tok_exact import Enc
T = pathlib.Path(sys.argv[1]); D = pathlib.Path(__file__).parent / "data"
NAMES = {"GPT-4o (o200k)": "o200k_base.tiktoken", "GPT-4 (cl100k)": "cl100k_base.tiktoken",
         "DictaLM 3.0": "dicta-il_DictaLM-3.0-24B-Base.tokenizer.json"}
HEB = re.compile("[\u05D0-\u05EA]"); MARK = re.compile("[\u05B0-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]")
def text(b):
    # HF byte-level files store tokens as GPT-2 byte-to-unicode strings; tok_exact's loader already maps them to bytes.
    # Census counts only tokens that are complete UTF-8 (fragments that cut a letter in half are excluded).
    try: return b.decode("utf-8")
    except UnicodeDecodeError: return ""
pointed = (D / "nikud_pointed.txt").read_text(encoding="utf-8").splitlines()
plain = (D / "nikud_plain.txt").read_text(encoding="utf-8").splitlines()
stems = "ספר בית ילד עיר מים שלום עבודה ממשלה מחשב חלון שולחן תלמיד מדינה רופא משפחה חבר כסף אוכל דרך עולם".split()
prefs = ["", "ה", "ו", "ב", "ל", "מ", "ש", "וה", "בה", "לה", "מה", "כש", "וכש", "ושב", "ומה"]
for name, f in NAMES.items():
    e = Enc(str(T / f)); print(f"== {name}")
    toks = [text(b) for b in set(e.ranks) | set(e.whole)]
    heb = [t for t in toks if HEB.search(t)]
    print(f"  census: tokens with a Hebrew letter (U+05D0-05EA) {len(heb)}; of these with a pointing mark {sum(1 for t in heb if MARK.search(t))}; "
          f"multi-letter {sum(1 for t in heb if len(HEB.findall(t)) > 1)}")
    cp, cq = sum(e.count(l) for l in pointed), sum(e.count(l) for l in plain)
    print(f"  nikud: pointed {cp}, plain {cq}, ratio {cp/cq:.2f}")
    if name.startswith("GPT-4o"):
        cats = {"mark only": 0, "letter+mark": 0, "letters only": 0, "byte fragment": 0, "other": 0}
        for l in pointed:
            for w in e.pat.findall(l):
                for p in e.pieces(w.encode("utf-8")):
                    try: s = p.decode("utf-8")
                    except UnicodeDecodeError: cats["byte fragment"] += 1; continue
                    m, h = bool(MARK.search(s)), bool(HEB.search(s))
                    cats["letter+mark" if m and h else "mark only" if m else "letters only" if h else "other"] += 1
        print("  pointed-token classes:", cats, "total", sum(cats.values()))
    row = []
    for p in prefs:
        row.append(f"{p or 'bare'}:{sum(e.count(' ' + p + s) for s in stems) / len(stems):.2f}")
    print("  prefix mean tokens/word:", " ".join(row))
    one = sum(1 for p in prefs[1:] for s in stems if e.count(" " + p + s) == 1)
    print(f"  single-token: bare {sum(e.count(' ' + s) == 1 for s in stems)}/{len(stems)}, prefixed {one}/{len(prefs[1:]) * len(stems)}; "
          f"' בית'={e.count(' בית')} ' ובבית'={e.count(' ובבית')}")
