#!/bin/sh
# Reproduce every number in README.md. Outputs go to results/.
set -e
cd "$(dirname "$0")"
T=tok
for c in heb eng; do
  for f in o200k_base.tiktoken cl100k_base.tiktoken dicta-il_DictaLM-3.0-24B-Base.tokenizer.json; do echo "$c $f $(python3 -I tok_exact.py $T/$f data/flores_$c.txt)"; done
  for f in mistralai_Mistral-7B-v0.1.tokenizer.json dicta-il_dictalm2.0.tokenizer.json; do echo "$c $f $(python3 -I sp_count.py $T/$f data/flores_$c.txt)"; done
done > results/flores_counts_mine.txt
python3 -I analyze.py $T > results/analyze.txt
echo "o200k on nikud_pointed.txt: approximate pre-tokenizer (bpe_count.py) $(python3 -I bpe_count.py $T/o200k_base.tiktoken data/nikud_pointed.txt), exact (tok_exact.py) $(python3 -I tok_exact.py $T/o200k_base.tiktoken data/nikud_pointed.txt)" > results/nikud_extra.txt
python3 -I marks.py $T/o200k_base.tiktoken >> results/nikud_extra.txt
cat results/flores_counts_mine.txt results/analyze.txt results/nikud_extra.txt
