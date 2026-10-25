# Download the tokenizer files and FLORES-101 rows into ./tok and ./data, and check sha256 against results/sha256.txt.
# Usage: python3 get_data.py
import hashlib, json, pathlib, sys, urllib.request
H = pathlib.Path(__file__).parent; TOK = H / "tok"; TOK.mkdir(exist_ok=True)
HF = "https://huggingface.co/{}/resolve/{}/tokenizer.json"
FILES = {
    "o200k_base.tiktoken": "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken",
    "cl100k_base.tiktoken": "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken",
    "mistralai_Mistral-7B-v0.1.tokenizer.json": HF.format("mistralai/Mistral-7B-v0.1", "27d67f1b5f57dc0953326b2601d68371d40ea8da"),
    "dicta-il_dictalm2.0.tokenizer.json": HF.format("dicta-il/dictalm2.0", "f8ab3208e95a7b44a9a2fbb9bbbdd8ea11be509d"),
    "dicta-il_DictaLM-3.0-24B-Base.tokenizer.json": HF.format("dicta-il/DictaLM-3.0-24B-Base", "6efc92259da9a242b937f9af3a099c18d3a127cb"),
}
ROWS = "https://datasets-server.huggingface.co/rows?dataset=gsarti/flores_101&config={}&split=devtest&offset=0&length=100"
want = dict(reversed(l.split()) for l in (H / "results/sha256.txt").read_text().splitlines())
for name, url in FILES.items():
    p = TOK / name
    if not p.exists():
        urllib.request.urlretrieve(url, p.with_suffix(".part"))  # rename only after a complete download
        p.with_suffix(".part").rename(p)
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    print(name, "OK" if got == want[name] else f"HASH MISMATCH {got}")
    if got != want[name]: sys.exit(1)
for c in ["heb", "eng"]:
    d = json.load(urllib.request.urlopen(ROWS.format(c)))
    rows = sorted(d["rows"], key=lambda r: r["row_idx"])
    text = "\n".join(r["row"]["sentence"] for r in rows) + "\n"
    (H / "data" / f"flores_{c}.txt").write_text(text, encoding="utf-8")
    got = hashlib.sha256(text.encode()).hexdigest()
    print(f"flores_{c}.txt", len(rows), "rows", "OK" if got == want[f"flores_{c}.txt"] else f"HASH MISMATCH {got}")
    if got != want[f"flores_{c}.txt"]: sys.exit(1)
