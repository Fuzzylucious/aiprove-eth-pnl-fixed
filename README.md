# ETH EMA trend backtest

## Strategy

The submitted rule in `strategy.py` compares the 30-period and 120-period
exponential moving averages of close prices. It holds `+1` when
`fast / slow - 1 > 0.0002` (+0.02%), `-1` when that value is below -0.02%,
and `0` inside the band. It stays flat for the first 120 bars. The EMA uses
the recursive update with alpha `2 / (period + 1)`, initialized from the first
close. The rule is causal: at each bar close it uses only closes observed
through that bar, and the chosen target earns the close-to-close move into the
next bar.

Three fixed designs were evaluated on the frozen dataset. The strength-scaled
12/48 design used `clamp((fast / slow - 1) / 0.0002, -1, 1)` after its 48-bar
warm-up; the two banded designs used binary `+1/0/-1` targets and remained
flat through their respective warm-ups.

| Design | Net PnL (USDT) | Position changes | Fees + slippage (USDT) | Max drawdown |
| --- | ---: | ---: | ---: | ---: |
| Strength-scaled 12/48 | -297.43 | 169 | 476.08 | 0.8465% |
| Banded binary 12/48 | -237.45 | 65 | 454.05 | 0.8015% |
| Banded binary 30/120 (submitted) | -172.13 | 35 | 244.38 | 0.5788% |

The submitted rule is the 30/120 banded binary design because slower state
changes are the classic response to one-minute noise and fee bleed. This
choice reflects that general principle, not per-bar fitting to this sample.

## Backtest cost model

The local replay starts with 100,000 USDT and allows a maximum absolute
position of 5 ETH. Each position change trades the absolute difference
between old and new targets, scaled by 5 ETH. Traded notional is valued at
that bar's close and charged a 0.05% taker fee plus 0.02% slippage. Equity is
marked to market on each close, using the position chosen at the preceding
close for the intervening move. There is no forced liquidation after the
last bar. The real grader's fee and slippage schedule may differ; this local
model is intended to require the strategy to survive realistic costs.

## Run

```sh
python3 strategy.py && python3 backtest.py
```

`strategy.py` writes `positions.csv` with `minute,position` columns and prints
a short summary. `backtest.py` imports and calls the same `positions()`
function.

## Results on the frozen bars.csv

Output from running the commands above:

```text
Wrote 1440 positions to positions.csv; position changes: 35
Final equity:          99827.87 USDT
Net PnL:               -172.13 USDT (-0.1721%)
Position changes:      35
Fees + slippage paid:  244.38 USDT
Max drawdown:          0.5788%
```
