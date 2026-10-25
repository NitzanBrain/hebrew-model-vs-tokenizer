# Which Hebrew points/marks (U+05B0-05C7) are not a single token on their own in a tokenizer.
# Usage: python3 -I marks.py <tokenizer file>
import sys, pathlib, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tok_exact import Enc
e = Enc(sys.argv[1])
print("Hebrew points/marks U+05B0-05C7 that are NOT a single token on their own:")
for cp in range(0x05B0, 0x05C8):
    n = len(e.pieces(chr(cp).encode()))
    if n > 1: print(" ", hex(cp), unicodedata.name(chr(cp), "?"), n)
