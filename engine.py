"""Dollar claims pay one dollar at T unless explicitly stated otherwise.

Rates are annual continuously compounded decimals; time is in years.
This module has no UI, network, or random state.
"""
from math import exp, isclose, isfinite


def discount(rate, years):
    if not all(isfinite(x) for x in (rate, years)) or years < 0:
        raise ValueError('Use finite rates and nonnegative time.')
    return exp(-rate * years)


def binary_position(price, quantity, rate, years, belief):
    if not 0 <= belief <= 1 or price < 0 or quantity < 0:
        raise ValueError('Belief must be in [0,1]; price and quantity nonnegative.')
    d = discount(rate, years)
    cost = quantity * price
    funding = cost / d
    return dict(discount=d, cost=cost, funding=funding,
                yes_profit=quantity-funding, no_profit=-funding,
                expected_profit=quantity*belief-funding,
                q=price/d if 0 <= price <= d else None)


def complete_set(prices, rate, years):
    if not prices or any(not isfinite(v) or v < 0 for v in prices):
        raise ValueError('Prices must be a nonempty list of nonnegative values.')
    d = discount(rate, years)
    total = sum(prices)
    gap = d-total
    return dict(discount=d, total=total, gap=gap,
                direction='balanced' if isclose(gap, 0, abs_tol=1e-9) else
                ('buy' if gap > 0 else 'sell'),
                normalized=[v/d for v in prices])


def probability_weights(probabilities, relative_weights, rate, years):
    """An explicitly specified positive pricing kernel, not inferred from quotes.

    M_i = D*w_i/sum(p_j*w_j); V_i=p_i*M_i; q_i=V_i/D.
    Scaling preserves E[M]=D for all slider settings.
    """
    p, w = list(probabilities), list(relative_weights)
    if len(p) != len(w) or not p or not isclose(sum(p), 1, abs_tol=1e-10):
        raise ValueError('Provide matched vectors and probabilities summing to one.')
    if any(not isfinite(x) or x < 0 for x in p) or any(not isfinite(x) or x <= 0 for x in w):
        raise ValueError('Probabilities must be nonnegative and weights positive.')
    d = discount(rate, years)
    z = sum(pi*wi for pi, wi in zip(p, w))
    m = [d*wi/z for wi in w]
    values = [pi*mi for pi, mi in zip(p, m)]
    return dict(discount=d, kernel=m, values=values, q=[v/d for v in values])


def gdp_hedge(p_low, bad_times_weight, rate, years, quantity,
              income_low=60.0, income_other=100.0):
    if quantity < 0:
        raise ValueError('Quantity cannot be negative.')
    model = probability_weights([p_low, 1-p_low], [bad_times_weight, 1], rate, years)
    price = model['values'][0]
    cost = quantity*price
    repayment = cost/model['discount']
    income = [income_low, income_other]
    net = [income_low+quantity-repayment, income_other-repayment]
    mean_before = p_low*income_low+(1-p_low)*income_other
    mean_after = p_low*net[0]+(1-p_low)*net[1]
    return dict(**model, price=price, cost=cost, repayment=repayment,
                income=income, net=net, mean_before=mean_before, mean_after=mean_after,
                expected_claim_profit=quantity*p_low-repayment,
                spread_before=abs(income_low-income_other), spread_after=abs(net[0]-net[1]))


def conversion(yes_bid, yes_ask, no_bid, no_ask, buy_cost, sell_cost):
    if not (0 <= yes_bid <= yes_ask <= 1 and 0 <= no_bid <= no_ask <= 1):
        raise ValueError('Each bid must be at most its ask, within [0,1].')
    if min(buy_cost, sell_cost) < 0:
        raise ValueError('Costs cannot be negative.')
    return dict(buy_merge=1-yes_ask-no_ask-buy_cost,
                split_sell=yes_bid+no_bid-1-sell_cost)


def sports_payoffs(home_goals, away_goals):
    """Regulation-time result; draws count as No on 'home wins'."""
    if min(home_goals, away_goals) < 0:
        raise ValueError('Goals cannot be negative.')
    return [int(home_goals > away_goals), int(home_goals == away_goals),
            int(home_goals < away_goals)]
