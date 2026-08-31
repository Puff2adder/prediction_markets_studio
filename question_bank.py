"""Knowledge-check questions with deterministic per-session shuffling."""

import random


QUESTIONS = [
    ("A Yes contract pays $1 when the event occurs. What does its paired No contract pay then?", ["$0", "$1", "The Yes price", "The discount factor"], "$0", "Yes and No are complementary state claims."),
    ("At maturity T, what does a complete Yes+No package pay?", ["$1 in either state", "$2 in either state", "$1 only if Yes occurs", "An uncertain amount"], "$1 in either state", "Exactly one of the two claims pays $1."),
    ("In general frictionless derivative theory, the present-value benchmark for a Yes+No package paying $1 at T is:", ["exp(−rT)", "1+rT", "exp(rT)", "The physical probability"], "exp(−rT)", "The package replicates a zero-coupon claim paying $1 at T."),
    ("A contract price divided by exp(−rT) is best described as:", ["A market-implied risk-adjusted probability", "A guaranteed physical frequency", "The contract's return", "An arbitrage profit"], "A market-implied risk-adjusted probability", "Prices need not reveal physical probabilities."),
    ("You think an event is more likely than the market-implied probability. Buying Yes is necessarily:", ["Speculation, not arbitrage", "A riskless arbitrage", "A hedge in every case", "A zero-cost position"], "Speculation, not arbitrage", "Your belief can be wrong and the payoff is state dependent."),
    ("Which item belongs in a well-designed settlement rule?", ["Authoritative data source and decision time", "The trader's private forecast", "A promise that prices are accurate", "A preferred trading strategy"], "Authoritative data source and decision time", "Objective settlement requires an observable source and cutoff."),
    ("In general derivative theory, if Yes+No costs more than the matching zero-coupon claim, the gross parity trade is to:", ["Sell Yes and No and buy the zero-coupon payoff", "Buy Yes and No", "Buy only Yes", "Ignore the guaranteed payoff"], "Sell Yes and No and buy the zero-coupon payoff", "The expensive package is sold against its cheaper replicating payoff."),
    ("Why might an apparent parity gap not be executable?", ["Fees, spreads, collateral, position limits, or shorting constraints", "Because Yes and No never sum to one", "Because probabilities cannot be compared", "Because all contracts are calls"], "Fees, spreads, collateral, position limits, or shorting constraints", "Market frictions can consume the gross gap or block the trade."),
    ("Four outcome claims are mutually exclusive but not exhaustive. Their prices should necessarily sum to exp(−rT):", ["False", "True", "Only when r is negative", "Only when all prices match"], "False", "An omitted state means the package need not pay $1 in every outcome."),
    ("A binary prediction claim most closely resembles which option payoff?", ["A cash-or-nothing digital option", "A standard call with unlimited upside", "A forward contract", "A zero-coupon bond in isolation"], "A cash-or-nothing digital option", "Its payoff jumps from zero to a fixed amount when a condition is met."),
    ("Compared with a digital call, a standard call above strike has payoff that:", ["Increases linearly with the underlying", "Stays fixed at $1", "Falls as the underlying rises", "Is always zero"], "Increases linearly with the underlying", "A call pays max(S_T−K,0)."),
    ("In the practice-token market maker, buying an outcome generally makes its displayed price:", ["Rise", "Fall", "Stay exactly fixed", "Become negative"], "Rise", "The automated market maker responds to demand with price impact."),
    ("A larger LMSR liquidity parameter generally produces:", ["Less price impact for the same trade", "More price impact for the same trade", "Prices that no longer sum to one", "A guaranteed profit"], "Less price impact for the same trade", "More liquidity makes the price curve flatter."),
    ("Which distinction is essential when interpreting a prediction-market price?", ["Risk-adjusted pricing versus physical belief", "Payoff versus strike only", "Coupon versus duration only", "Spot versus storage only"], "Risk-adjusted pricing versus physical belief", "Risk preferences and frictions can separate price-implied and physical probabilities."),
    ("A contract costs $0.40 and pays $1 on Yes. The buyer's profit if No occurs is:", ["−$0.40", "$0", "$0.40", "$1.00"], "−$0.40", "Payoff is zero, but the purchase price was paid."),
    ("The sum of displayed multi-outcome market-maker prices should be:", ["1", "The liquidity parameter", "The number of outcomes", "The trading volume"], "1", "The prices are normalized state weights."),
    ("Which statement is most accurate?", ["A prediction price can aggregate information without being a perfect forecast", "A prediction price is always the true probability", "Prediction contracts have no settlement risk", "A high price guarantees the event"], "A prediction price can aggregate information without being a perfect forecast", "Risk, frictions, ambiguity, and noise all affect interpretation."),
    ("On a platform where $1 of collateral creates one Yes plus one No, the operational complete-set benchmark is:", ["$1", "exp(−rT)", "$2", "The Yes price alone"], "$1", "Creation and merge operate against the full dollar of locked collateral."),
    ("On Polymarket, simultaneous executable bids are $0.58 for Yes and $0.47 for No. Ignoring frictions, the creation-and-sale gross gap is:", ["$0.05", "$0.47", "$0.95", "exp(−rT)"], "$0.05", "Split $1 into the pair and sell the shares at both bids for a combined $1.05."),
    ("Relative to the textbook present-value benchmark, locking a full $1 until T creates:", ["A funding opportunity cost", "A guaranteed extra payoff", "No economic difference when rates are positive", "A second Yes token"], "A funding opportunity cost", "The collateral cannot simultaneously earn the outside risk-free return while locked."),
    ("In Kalshi's complementary order book, a Yes bid of $0.58 implies a No ask of:", ["$0.42", "$0.58", "$1.58", "$0.00"], "$0.42", "The complementary ask is one dollar minus the bid."),
    ("If Kalshi's best Yes bid is $0.58 and best No bid is $0.37, the implied spread is:", ["$0.05", "$0.95", "$0.21", "$0.00"], "$0.05", "The spread is $1 − $0.58 − $0.37."),
    ("If purported simultaneous Kalshi Yes and No best bids sum to more than $1, the most useful first conclusion is:", ["The inputs describe a crossed book that should match", "A persistent riskless profit must be available", "Both asks equal the bids", "The terminal payoff changed"], "The inputs describe a crossed book that should match", "Opposing bids that jointly fund more than $1 should not remain as independent executable best bids."),
]


def shuffled_choices(question_index: int, seed: int) -> list[str]:
    choices = list(QUESTIONS[question_index][1])
    random.Random(seed + 104729 * question_index).shuffle(choices)
    return choices
