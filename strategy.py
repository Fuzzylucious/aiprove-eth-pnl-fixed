#!/usr/bin/env python3
"""Fixed EMA trend strategy for the frozen ETH bar format."""

import csv
from pathlib import Path


FAST_PERIOD = 30
SLOW_PERIOD = 120
NO_TRADE_BAND = 0.0002


def _read_bars(path):
    with open(path, newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def positions(bars):
    """Return one causal target position per bar, in the range [-1, 1]."""
    result = []
    fast_ema = slow_ema = None
    fast_alpha = 2.0 / (FAST_PERIOD + 1)
    slow_alpha = 2.0 / (SLOW_PERIOD + 1)

    for index, bar in enumerate(bars):
        close = float(bar["close"])
        if fast_ema is None:
            fast_ema = slow_ema = close
        else:
            fast_ema += fast_alpha * (close - fast_ema)
            slow_ema += slow_alpha * (close - slow_ema)

        if index < SLOW_PERIOD:
            result.append(0.0)
            continue

        relative_trend = fast_ema / slow_ema - 1.0
        if relative_trend > NO_TRADE_BAND:
            result.append(1.0)
        elif relative_trend < -NO_TRADE_BAND:
            result.append(-1.0)
        else:
            result.append(0.0)

    return result


def main():
    bars = _read_bars(Path(__file__).with_name("bars.csv"))
    targets = positions(bars)
    output_path = Path(__file__).with_name("positions.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(("minute", "position"))
        for bar, position in zip(bars, targets):
            writer.writerow((bar["minute"], f"{position:.10f}"))
    changes = sum(a != b for a, b in zip([0.0] + targets[:-1], targets))
    print(f"Wrote {len(targets)} positions to {output_path.name}; position changes: {changes}")


if __name__ == "__main__":
    main()
