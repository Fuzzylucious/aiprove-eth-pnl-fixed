#!/usr/bin/env python3
"""Replay strategy.py with a simple close-to-close, costed spot model."""

import csv
from pathlib import Path

from strategy import positions


STARTING_EQUITY = 100_000.0
MAX_POSITION_ETH = 5.0
TAKER_FEE_RATE = 0.0005
SLIPPAGE_RATE = 0.0002


def read_bars(path):
    with open(path, newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def run_backtest(bars):
    targets = positions(bars)
    closes = [float(bar["close"]) for bar in bars]
    equity = STARTING_EQUITY
    peak_equity = equity
    max_drawdown = 0.0
    previous_position = 0.0
    changes = 0
    costs_paid = 0.0

    for index, (target, close) in enumerate(zip(targets, closes)):
        if target != previous_position:
            traded_eth = abs(target - previous_position) * MAX_POSITION_ETH
            cost = traded_eth * close * (TAKER_FEE_RATE + SLIPPAGE_RATE)
            equity -= cost
            costs_paid += cost
            changes += 1

        if index + 1 < len(closes):
            held_eth = target * MAX_POSITION_ETH
            equity += held_eth * (closes[index + 1] - close)

        peak_equity = max(peak_equity, equity)
        if peak_equity > 0:
            max_drawdown = max(max_drawdown, (peak_equity - equity) / peak_equity)
        previous_position = target

    net_pnl = equity - STARTING_EQUITY
    return {
        "final_equity": equity,
        "net_pnl": net_pnl,
        "net_pnl_pct": net_pnl / STARTING_EQUITY * 100.0,
        "position_changes": changes,
        "costs_paid": costs_paid,
        "max_drawdown_pct": max_drawdown * 100.0,
    }


def main():
    bars = read_bars(Path(__file__).with_name("bars.csv"))
    result = run_backtest(bars)
    print(f"Final equity:          {result['final_equity']:.2f} USDT")
    print(f"Net PnL:               {result['net_pnl']:.2f} USDT ({result['net_pnl_pct']:.4f}%)")
    print(f"Position changes:      {result['position_changes']}")
    print(f"Fees + slippage paid:  {result['costs_paid']:.2f} USDT")
    print(f"Max drawdown:          {result['max_drawdown_pct']:.4f}%")


if __name__ == "__main__":
    main()
