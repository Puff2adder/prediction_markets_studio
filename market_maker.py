"""A small logarithmic market scoring rule simulator using practice tokens."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


def _validate(quantities: Sequence[float], liquidity: float) -> np.ndarray:
    q = np.asarray(quantities, dtype=float)
    if q.ndim != 1 or q.size < 2:
        raise ValueError("At least two outcome quantities are required.")
    if liquidity <= 0:
        raise ValueError("Liquidity must be positive.")
    return q


def outcome_prices(quantities: Sequence[float], liquidity: float) -> np.ndarray:
    q = _validate(quantities, liquidity)
    scaled = q / liquidity
    weights = np.exp(scaled - np.max(scaled))
    return weights / weights.sum()


def cost(quantities: Sequence[float], liquidity: float) -> float:
    q = _validate(quantities, liquidity)
    scaled = q / liquidity
    maximum = float(np.max(scaled))
    return liquidity * (maximum + math.log(float(np.exp(scaled - maximum).sum())))


def trade_cost(
    quantities: Sequence[float], outcome_index: int, shares: float, liquidity: float
) -> tuple[float, np.ndarray, np.ndarray]:
    q = _validate(quantities, liquidity)
    if outcome_index < 0 or outcome_index >= len(q):
        raise IndexError("Outcome index is out of range.")
    before = outcome_prices(q, liquidity)
    after_q = q.copy()
    after_q[outcome_index] += shares
    paid = cost(after_q, liquidity) - cost(q, liquidity)
    return paid, after_q, outcome_prices(after_q, liquidity)
