# Count tokens for SentencePiece-style BPE tokenizer.json files (Llama/Mistral-7B family: ▁ for spaces, char-level merges, byte_fallback).
# Run: python3 -I sp_count.py <tokenizer.json> <text file, one segment per line>
import json, sys

def load(path):
    t = json.load(open(path, encoding="utf-8"))
    m = t["model"]
    ranks = {}
    for i, mg in enumerate(m["merges"]):
        a, b = mg if isinstance(mg, list) else mg.split(" ")
        ranks.setdefault((a, b), i)
    return ranks, set(m["vocab"])

def count(text, ranks, vocab):
    if not text:
        return 0
    parts = list("▁" + text.replace(" ", "▁"))
    while len(parts) > 1:
        best, idx = None, -1
        for i in range(len(parts) - 1):
            r = ranks.get((parts[i], parts[i + 1]))
            if r is not None and (best is None or r < best):
                best, idx = r, i
        if idx < 0:
            break
        parts[idx:idx + 2] = [parts[idx] + parts[idx + 1]]
    return sum(1 if p in vocab else len(p.encode("utf-8")) for p in parts)  # byte_fallback

if __name__ == "__main__":
    ranks, vocab = load(sys.argv[1])
    print(sum(count(l, ranks, vocab) for l in open(sys.argv[2], encoding="utf-8").read().splitlines()))
