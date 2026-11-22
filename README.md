# The Sunday Blast — news-image-20261122

A one-image summary of the world news of **Sunday 22 November 2026**, drawn
as a tabloid front page by a pure Python 3 (standard library only) program.

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/SURAXY1/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/SURAXY1/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

## What the page reports

- **Lead — COP31, Antalya (Reuters):** the climate talks approach a final
  deal on Sunday after blowing past the Friday deadline; the COP31
  presidents (Australia and Türkiye) table a package text, President Murat
  Kurum calls it "a text which all the parties can agree upon", objections
  close at 03:00 GMT and the approval session is set for 06:00 GMT, with
  nearly 200 delegations weighing the text.
- **The fossil-fuel fight (Reuters):** a Thursday draft stripped all
  mentions of fossil fuels — coal, oil and gas — and dropped the
  $120bn-a-year adaptation-finance target, replaced by a call to at least
  triple adaptation finance by 2035; EU negotiator Wopke Hoekstra: "a good
  deal or no deal".
- **Germany (Reuters):** IG Metall calls a 24-hour strike for Monday —
  23,000 workers at 19 companies in northern Germany, including
  Mercedes-Benz, Meyer Werft and Siemens Gamesa; the union demands a 5%
  wage increase, and 12,300 workers struck on Friday.
- **Liberia (AFP):** 25 migrants deported from the US, including two
  women, arrive in Liberia, a Liberian commission confirms; the US–Liberia
  deal allows up to 1,200 third-country deportees over 12 months.

## How it works

`main.py` paints the front page pixel by pixel into an RGB framebuffer
using a hand-built 5x7 block typeface, encodes it as a PNG with `zlib`,
and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`. No network, no input
files, no clock, no randomness — every run produces byte-identical
output (1024×1024 PNG, ~20 KB).

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
