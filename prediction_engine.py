"""Financial calculations for the Prediction Market Studio.

Prices are per $1 of promised payoff. Rates are continuously compounded.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


TOLERANCE = 1e-10


def discount_factor(rate: float, maturity: float) -> float:
    if maturity < 0:
        raise ValueError("Maturity cannot be negative.")
    return math.exp(-rate * maturity)


def binary_payoff(event_occurs: bool, side: str = "yes") -> float:
    side = side.lower()
    if side not in {"yes", "no"}:
        raise ValueError("Side must be 'yes' or 'no'.")
    return float(event_occurs if side == "yes" else not event_occurs)


def position_profit(
    event_occurs: bool,
    side: str,
    price: float,
    quantity: float = 1.0,
    direction: str = "buy",
) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative.")
    sign = {"buy": 1.0, "sell": -1.0}.get(direction.lower())
    if sign is None:
        raise ValueError("Direction must be 'buy' or 'sell'.")
    payoff = binary_payoff(event_occurs, side)
    return sign * quantity * (payoff - price)


def implied_probability(
    price: float,
    rate: float,
    maturity: float,
    convention: str = "discounted",
) -> float:
    """Normalize price by the selected complete-set benchmark."""
    return price / complete_set_benchmark(rate, maturity, convention)


def expected_profit(
    subjective_probability: float,
    side: str,
    price: float,
    quantity: float = 1.0,
    direction: str = "buy",
) -> float:
    if not 0 <= subjective_probability <= 1:
        raise ValueError("Probability must lie between zero and one.")
    expected_payoff = subjective_probability if side.lower() == "yes" else 1 - subjective_probability
    sign = {"buy": 1.0, "sell": -1.0}.get(direction.lower())
    if sign is None:
        raise ValueError("Direction must be 'buy' or 'sell'.")
    return sign * quantity * (expected_payoff - price)


@dataclass(frozen=True)
class ParityResult:
    package_price: float
    benchmark_price: float
    gross_gap: float
    net_profit: float
    action: str
    feasible: bool


@dataclass(frozen=True)
class CollateralBookResult:
    creation_gross_gap: float
    merge_gross_gap: float
    creation_net_gap: float
    merge_net_gap: float


def collateral_book_gaps(
    yes_bid: float,
    no_bid: float,
    yes_ask: float,
    no_ask: float,
    cost_per_leg: float = 0.0,
) -> CollateralBookResult:
    """Executable complete-set gaps for a split/merge token platform."""
    if min(yes_bid, no_bid, yes_ask, no_ask, cost_per_leg) < 0:
        raise ValueError("Quotes and costs cannot be negative.")
    if yes_bid > yes_ask or no_bid > no_ask:
        raise ValueError("Each bid must be no greater than its ask.")
    creation = yes_bid + no_bid - 1.0
    merge = 1.0 - yes_ask - no_ask
    return CollateralBookResult(
        creation_gross_gap=creation,
        merge_gross_gap=merge,
        creation_net_gap=creation - 2 * cost_per_leg,
        merge_net_gap=merge - 2 * cost_per_leg,
    )


@dataclass(frozen=True)
class KalshiBookResult:
    yes_bid: float
    no_bid: float
    yes_ask: float
    no_ask: float
    spread: float
    crossed: bool


def kalshi_complementary_book(yes_bid: float, no_bid: float) -> KalshiBookResult:
    """Derive Kalshi-style complementary asks from the two bid books."""
    if not (0 <= yes_bid <= 1 and 0 <= no_bid <= 1):
        raise ValueError("Bids must lie between zero and one.")
    spread = 1.0 - yes_bid - no_bid
    return KalshiBookResult(
        yes_bid=yes_bid,
        no_bid=no_bid,
        yes_ask=1.0 - no_bid,
        no_ask=1.0 - yes_bid,
        spread=spread,
        crossed=spread < -TOLERANCE,
    )


def complete_set_benchmark(
    rate: float, maturity: float, convention: str = "discounted"
) -> float:
    """Price benchmark for a complete set under the selected market convention.

    ``discounted`` is the textbook frictionless value of a date-T dollar.
    ``full_collateral`` is the creation/merge amount on a platform that locks $1.
    """
    if convention == "discounted":
        return discount_factor(rate, maturity)
    if convention == "full_collateral":
        return 1.0
    raise ValueError("Convention must be 'discounted' or 'full_collateral'.")


def yes_no_parity(
    yes_price: float,
    no_price: float,
    rate: float,
    maturity: float,
    transaction_cost_per_contract: float = 0.0,
    shorting_allowed: bool = True,
    convention: str = "discounted",
) -> ParityResult:
    """Compare Yes+No with its complete-set benchmark."""
    if min(yes_price, no_price, transaction_cost_per_contract) < 0:
        raise ValueError("Prices and transaction costs cannot be negative.")
    package = yes_price + no_price
    benchmark = complete_set_benchmark(rate, maturity, convention)
    gap = package - benchmark
    costs = 2 * transaction_cost_per_contract
    if abs(gap) <= TOLERANCE:
        return ParityResult(package, benchmark, gap, -costs, "Prices satisfy parity.", True)
    if gap > 0:
        if convention == "full_collateral":
            feasible = True
            action = "Split $1 of collateral into Yes and No; sell both shares."
        else:
            feasible = shorting_allowed
            action = "Sell Yes and No; buy the $1 zero-coupon payoff."
    else:
        feasible = True
        if convention == "full_collateral":
            action = "Buy Yes and No; merge the complete set back into $1 of collateral."
        else:
            action = "Buy Yes and No; finance them against the $1 zero-coupon payoff."
    return ParityResult(package, benchmark, gap, abs(gap) - costs, action, feasible)


def complete_market_gap(
    prices: Iterable[float],
    rate: float,
    maturity: float,
    convention: str = "discounted",
) -> float:
    values = list(prices)
    if not values or min(values) < 0:
        raise ValueError("Provide one or more nonnegative outcome prices.")
    return sum(values) - complete_set_benchmark(rate, maturity, convention)


def digital_payoff(terminal_price: float, strike: float) -> float:
    return float(terminal_price > strike)


def call_payoff(terminal_price: float, strike: float) -> float:
    return max(terminal_price - strike, 0.0)
