# Exact-pattern BPE encoder: python3 -I tok_exact.py <tokenizer file> <text file>  → total token count
# Uses pretok.py (exact pre-tokenizer patterns) + byte-level BPE from bpe_count.py.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bpe_count import load
from pretok import pattern

class Enc:
    def __init__(self, path):
        loaded = load(path)
        self.ranks, self.whole = loaded if isinstance(loaded, tuple) else (loaded, frozenset())
        self.pat = pattern(path)

    def pieces(self, piece):
        if piece in self.whole:
            return [piece]
        parts = [piece[i:i + 1] for i in range(len(piece))]
        while len(parts) > 1:
            best, idx = None, -1
            for i in range(len(parts) - 1):
                r = self.ranks.get(parts[i] + parts[i + 1])
                if r is not None and (best is None or r < best):
                    best, idx = r, i
            if idx < 0:
                break
            parts[idx:idx + 2] = [parts[idx] + parts[idx + 1]]
        return parts

    def encode(self, text):
        """Token ids (tiktoken files) — for HF files ids are merge-ranks, only good for counting."""
        return [self.ranks.get(p) for w in self.pat.findall(text) for p in self.pieces(w.encode("utf-8"))]

    def count(self, text):
        return sum(len(self.pieces(w.encode("utf-8"))) for w in self.pat.findall(text))

if __name__ == "__main__":
    e = Enc(sys.argv[1])
    print(sum(e.count(l) for l in open(sys.argv[2], encoding="utf-8").read().splitlines()))
