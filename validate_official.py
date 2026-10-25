# Cross-check my pure-Python counts against the official libraries (tiktoken, Hugging Face tokenizers).
# Usage: python validate_official.py <dir with tokenizer files>   (needs: pip install tiktoken tokenizers)
import sys, pathlib, tiktoken
from tokenizers import Tokenizer
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tok_exact import Enc
import sp_count
T = pathlib.Path(sys.argv[1]); D = pathlib.Path(__file__).parent / "data"
texts = {f: (D / f).read_text(encoding="utf-8").splitlines() for f in ["flores_heb.txt", "flores_eng.txt", "nikud_pointed.txt", "nikud_plain.txt"]}
stems = "ספר בית ילד עיר מים שלום עבודה ממשלה מחשב חלון שולחן תלמיד מדינה רופא משפחה חבר כסף אוכל דרך עולם".split()
prefs = ["", "ה", "ו", "ב", "ל", "מ", "ש", "וה", "בה", "לה", "מה", "כש", "וכש", "ושב", "ומה"]
words = [" " + p + s for p in prefs for s in stems]
bad = 0
for f, name in [("o200k_base.tiktoken", "o200k_base"), ("cl100k_base.tiktoken", "cl100k_base"),
                ("dicta-il_DictaLM-3.0-24B-Base.tokenizer.json", None),
                ("mistralai_Mistral-7B-v0.1.tokenizer.json", "sp"), ("dicta-il_dictalm2.0.tokenizer.json", "sp")]:
    if name == "sp":
        ranks, vocab = sp_count.load(str(T / f)); mine = lambda s: sp_count.count(s, ranks, vocab)
    else:
        e = Enc(str(T / f)); mine = e.count
    if name and name != "sp":
        enc = tiktoken.get_encoding(name); off = lambda s: len(enc.encode_ordinary(s))
    else:
        tk = Tokenizer.from_file(str(T / f)); off = lambda s: len(tk.encode(s, add_special_tokens=False).ids) if s else 0
    for tn, lines in texts.items():
        a, b = sum(map(mine, lines)), sum(map(off, lines))
        bad += a != b; print(f"{f:48s} {tn:18s} mine {a:6d} official {b:6d} {'OK' if a == b else 'DIFF'}")
    d = sum(mine(w) != off(w) for w in words)
    bad += d > 0; print(f"{f:48s} prefix words: {d} of {len(words)} differ")
print("ALL MATCH" if bad == 0 else f"{bad} mismatching checks")
