"""Prediction Market Studio - Version 1.0."""

from __future__ import annotations

import secrets

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from challenge_bank import CHALLENGES
from market_maker import outcome_prices, trade_cost
from prediction_engine import (
    call_payoff,
    collateral_book_gaps,
    complete_set_benchmark,
    complete_market_gap,
    digital_payoff,
    discount_factor,
    expected_profit,
    implied_probability,
    kalshi_complementary_book,
    position_profit,
    yes_no_parity,
)
from question_bank import QUESTIONS, shuffled_choices
from ui import concept, configure_page, hero, success, warning, why


configure_page()
from studio_theme import apply_studio_theme, style_plotly, studio_line_chart
apply_studio_theme()


def initialize_state():
    st.session_state.setdefault("quiz_seed", secrets.randbits(63))
    st.session_state.setdefault("challenge_index", 0)
    st.session_state.setdefault("challenge_attempted", set())
    st.session_state.setdefault("lmsr_q", np.zeros(4))
    st.session_state.setdefault("lmsr_cash", 100.0)
    st.session_state.setdefault("lmsr_log", [])


def money(value):
    return f"-${abs(value):,.3f}" if value < 0 else f"${value:,.3f}"


def calculation_table(rows):
    """Display an auditable three-column calculation trail."""
    st.dataframe(
        pd.DataFrame(rows, columns=["Step", "Arithmetic", "Result and economic meaning"]),
        hide_index=True,
        width="stretch",
    )


def payoff_chart(yes_price, no_price, direction, side, quantity):
    states = ["No occurs", "Yes occurs"]
    profits = [
        position_profit(False, side, yes_price if side == "yes" else no_price, quantity, direction),
        position_profit(True, side, yes_price if side == "yes" else no_price, quantity, direction),
    ]
    fig = go.Figure(go.Bar(x=states, y=profits, marker_color=["#d15c3d", "#6b3ec7"]))
    fig.add_hline(y=0, line_color="#22205d")
    fig.update_layout(template="plotly_white", height=360, yaxis_title="Profit at settlement, $", margin=dict(l=20, r=20, t=25, b=20))
    return fig


def digital_call_chart(strike):
    terminal = np.linspace(max(0, strike - 40), strike + 60, 251)
    digital = [digital_payoff(s, strike) for s in terminal]
    call = [call_payoff(s, strike) for s in terminal]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=terminal, y=digital, name="Digital: $1 if Sₜ > K", line=dict(width=4, color="#6b3ec7")))
    fig.add_trace(go.Scatter(x=terminal, y=call, name="Standard call: max(Sₜ−K, 0)", yaxis="y2", line=dict(width=3, color="#e3a315")))
    fig.add_vline(x=strike, line_dash="dash", line_color="#d15c3d", annotation_text=f"K = {strike:g}")
    fig.update_layout(template="plotly_white", height=420, xaxis_title="Underlying value at expiration, Sₜ", yaxis=dict(title="Digital payoff, $"), yaxis2=dict(title="Standard call payoff, $", overlaying="y", side="right"), legend=dict(orientation="h", y=1.12), margin=dict(l=20, r=20, t=55, b=20))
    return fig


initialize_state()

st.sidebar.title("Prediction Market Studio")
st.sidebar.caption("Version 1.0 · hypothetical educational contracts")
page = st.sidebar.radio(
    "Learning laboratory",
    [
        "Studio orientation",
        "1 · Contract anatomy",
        "2 · Payoff and profit",
        "3 · Theory and platform practice",
        "4 · Price and belief",
        "5 · Multi-outcome markets",
        "6 · Practice-token market maker",
        "7 · Digital-option bridge",
        "8 · Applied challenges",
        "9 · Knowledge check",
    ],
)
st.sidebar.divider()
st.sidebar.caption("No live odds, money, accounts, grades, or personal data are used. All examples are fictional or explicitly hypothetical.")


if page == "Studio orientation":
    st.title("Prediction Market Studio")
    hero("Trade claims about uncertain events", "Start with an exact settlement rule, map every state to a payoff, then decide whether a price reflects replication, belief, risk, or market frictions.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Binary payoff", "$1 or $0")
    c2.metric("Collateral identity", "Yes + No ↔ $1")
    c3.metric("Practice modes", "9")
    c4.metric("Live market data", "None")
    st.subheader("Learning objectives")
    st.markdown(
        """
        By the end, you should be able to:

        1. write settlement rules that make a prediction claim objectively verifiable;
        2. distinguish payoff from profit for long and short Yes and No positions;
        3. contrast textbook present-value replication, Polymarket's $1 split/merge rule, and Kalshi's complementary order book;
        4. distinguish a market-implied risk-adjusted probability from a physical belief;
        5. explain how liquidity, fees, shorting limits, collateral, and ambiguity affect prices; and
        6. connect binary contracts to cash-or-nothing digital options.
        """
    )
    left, right = st.columns(2)
    with left:
        concept("Learning sequence", "Economic question → settlement rule → state payoff → price and profit → replication → interpretation → market design.")
    with right:
        warning("Educational scope", "Practice tokens are not money. The studio does not recommend wagers or investments and does not claim that a contract price is a true probability.")
    why("Prediction markets are compact laboratories for contingent claims. They make state-dependent payoffs, replication, information aggregation, and market frictions unusually visible.")


elif page == "1 · Contract anatomy":
    st.title("1 · Contract anatomy")
    hero("A clear payoff begins with a clear event", "A number cannot be interpreted until the event, source, deadline, and exceptional cases are pinned down.")
    event = st.text_input("Event statement", "Fictional Northbridge University cancels all in-person classes next Friday")
    source = st.text_input("Authoritative source", "Official Northbridge emergency-status webpage")
    deadline = st.text_input("Determination time and time zone", "6:00 a.m. Eastern Time next Friday")
    edge = st.text_area("Exceptional cases", "Remote instruction counts as cancellation; a delayed opening does not; all campuses must be covered.")
    if st.button("Build the settlement rule", type="primary"):
        if all(value.strip() for value in (event, source, deadline, edge)):
            success("Draft settlement rule", f"Yes pays $1 if **{event}**, as reported by **{source}** at **{deadline}**. **{edge}** Otherwise, No pays $1.")
        else:
            warning("Rule incomplete", "Complete the event, source, determination time, and exceptional-case fields.")
    st.subheader("Misconception check")
    st.info("A contract can have simple arithmetic but severe settlement risk. Words such as “release,” “cancel,” “win,” and “inflation” usually need operational definitions.")


elif page == "2 · Payoff and profit":
    st.title("2 · Payoff and profit")
    hero("The payoff is not the profit", "A correct state payoff is the beginning; the acquisition price and position direction determine profit.")
    c1, c2, c3, c4 = st.columns(4)
    yes_price = c1.slider("Yes price ($)", 0.0, 1.0, 0.58, 0.01)
    no_price = c2.slider("No price ($)", 0.0, 1.0, 0.42, 0.01)
    side_label = c3.selectbox("Claim", ["Yes", "No"])
    direction = c4.selectbox("Position", ["Buy", "Sell"])
    quantity = st.number_input("Number of contracts", 1, 100, 1)
    side = side_label.lower()
    price = yes_price if side == "yes" else no_price
    rows = []
    for occurs, state in [(False, "No occurs"), (True, "Yes occurs")]:
        payoff = float(occurs if side == "yes" else not occurs)
        if direction == "Sell":
            payoff *= -1
        rows.append({"State": state, "Position payoff ($)": quantity * payoff, "Initial cash flow ($)": (-1 if direction == "Buy" else 1) * quantity * price, "Profit at settlement ($)": position_profit(occurs, side, price, quantity, direction.lower())})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.plotly_chart(style_plotly(payoff_chart(yes_price, no_price, direction.lower(), side, quantity)), key="payoff_profit_chart", width="stretch", theme=None)
    concept("Read the signs", "Buying creates a negative initial cash flow and a nonnegative payoff. Selling reverses both cash flows and can create a settlement liability.")


elif page == "3 · Theory and platform practice":
    st.title("3 · Theory and platform practice")
    hero("The payoff identity survives; the trading mechanism changes", "Compare a frictionless textbook market with Polymarket's split/merge tokens and Kalshi's complementary event-contract order book.")
    regime = st.radio(
        "Choose the institutional setting",
        ["Textbook theory", "Polymarket", "Kalshi"],
        horizontal=True,
    )
    c1, c2 = st.columns(2)
    maturity = c1.number_input("Maturity T (years)", 0.0, 10.0, 0.5, 0.25, key="parity_maturity")
    rate = c2.number_input("Continuous rate r (%)", -10.0, 30.0, 4.0, 0.25, key="parity_rate") / 100
    df = discount_factor(rate, maturity)
    st.markdown("#### Start with the funding calculation")
    calculation_table(
        [
            ("1. Terminal complete-set payoff", "$1.000 at date T", "Exactly one of Yes or No pays $1."),
            ("2. Continuous discount factor", f"exp(−{rate:.4f} × {maturity:.2f})", f"{df:.4f}"),
            ("3. Textbook present value", f"$1.000 × {df:.4f}", f"{money(df)} today"),
            ("4. Full-collateral funding wedge", f"$1.000 − {df:.4f}", f"{money(1-df)} of foregone interest"),
        ]
    )

    if regime == "Textbook theory":
        concept("Benchmark", "In a frictionless financial market, Yes + No pays one dollar at T and therefore has date-0 value e<sup>−rT</sup>.")
        c1, c2, c3 = st.columns(3)
        yes_price = c1.number_input("Yes price ($)", 0.0, 2.0, 0.58, 0.01, key="theory_yes")
        no_price = c2.number_input("No price ($)", 0.0, 2.0, 0.47, 0.01, key="theory_no")
        fee = c3.number_input("Implementation cost per leg ($)", 0.0, 0.5, 0.005, 0.005, key="theory_fee", format="%.3f")
        shorting = st.checkbox("Short selling is permitted", value=True, key="theory_short")
        result = yes_no_parity(yes_price, no_price, rate, maturity, fee, shorting, "discounted")
        st.markdown("#### Follow the textbook comparison")
        calculation_table(
            [
                ("1. Price the complete market package", f"{yes_price:.3f} + {no_price:.3f}", f"{money(result.package_price)} for Yes + No"),
                ("2. Price the replicating date-T dollar", f"1.000 × exp(−{rate:.4f} × {maturity:.2f})", f"{money(result.benchmark_price)}"),
                ("3. Compute the signed pricing gap", f"{result.package_price:.4f} − {result.benchmark_price:.4f}", f"{money(result.gross_gap)}; positive means Yes + No is expensive"),
                ("4. Compute two-leg implementation costs", f"2 × {fee:.3f}", f"{money(2*fee)}"),
                ("5. Compute modeled net opportunity", f"|{result.gross_gap:.4f}| − {2*fee:.4f}", f"{money(result.net_profit)} before other frictions"),
            ]
        )
        if st.button("Test the textbook trade", type="primary"):
            if not result.feasible:
                warning("Trade blocked", "The overpriced package trade requires short selling under these assumptions.")
            elif result.net_profit > 0:
                success("Positive modeled gap", f"{result.action} Net initial surplus after entered costs: {money(result.net_profit)}.")
            else:
                warning("No positive net gap", "The entered implementation costs absorb the gross pricing difference.")
        st.caption("This benchmark assumes tradable borrowing/lending at r, frictionless shorting, and no collateral wedge.")

    elif regime == "Polymarket":
        concept("Operational benchmark", "One dollar of pUSD collateral can be split into one Yes token plus one No token; an equal pair can be merged back into one dollar. Therefore the platform creation/merge benchmark is $1, not e<sup>−rT</sup>.")
        st.markdown("#### Enter simultaneous executable quotes")
        c1, c2, c3, c4 = st.columns(4)
        yes_bid = c1.number_input("Yes bid ($)", 0.0, 1.0, 0.58, 0.01)
        no_bid = c2.number_input("No bid ($)", 0.0, 1.0, 0.47, 0.01)
        yes_ask = c3.number_input("Yes ask ($)", 0.0, 1.0, 0.60, 0.01)
        no_ask = c4.number_input("No ask ($)", 0.0, 1.0, 0.49, 0.01)
        fee = st.number_input("Estimated fee and execution cost per leg ($)", 0.0, 0.5, 0.005, 0.005, key="poly_fee", format="%.3f")
        try:
            book = collateral_book_gaps(yes_bid, no_bid, yes_ask, no_ask, fee)
            st.markdown("#### Follow both executable complete-set trades")
            calculation_table(
                [
                    ("1. Post collateral and split", "$1.000 → 1 Yes + 1 No", "One complete token set is created."),
                    ("2. Sell the created Yes", f"1 × {yes_bid:.3f}", f"Receive {money(yes_bid)} at the Yes bid"),
                    ("3. Sell the created No", f"1 × {no_bid:.3f}", f"Receive {money(no_bid)} at the No bid"),
                    ("4. Add sale proceeds", f"{yes_bid:.3f} + {no_bid:.3f}", f"Receive {money(yes_bid+no_bid)}"),
                    ("5. Creation-and-sale gross gap", f"({yes_bid:.3f} + {no_bid:.3f}) − 1.000", f"{money(book.creation_gross_gap)}"),
                    ("6. Subtract two-leg costs", f"{book.creation_gross_gap:.3f} − 2 × {fee:.3f}", f"{money(book.creation_net_gap)} after entered costs"),
                    ("7. Cost of buying a complete set", f"{yes_ask:.3f} + {no_ask:.3f}", f"Pay {money(yes_ask+no_ask)} at the asks"),
                    ("8. Buy-and-merge gross gap", f"1.000 − ({yes_ask:.3f} + {no_ask:.3f})", f"{money(book.merge_gross_gap)}; positive would favor buying and merging"),
                    ("9. Buy-and-merge after costs", f"{book.merge_gross_gap:.3f} − 2 × {fee:.3f}", f"{money(book.merge_net_gap)}"),
                ]
            )
            if book.creation_net_gap > 0:
                success("Creation-and-sale opportunity under entered quotes", "Lock $1, split it into Yes and No, then sell both at the simultaneous bids. With $0.58 + $0.47, the gross gap is $0.05 before fees and execution costs.")
            elif book.merge_net_gap > 0:
                success("Purchase-and-merge opportunity under entered quotes", "Buy Yes and No at the simultaneous asks, then merge the pair into $1 of collateral.")
            else:
                warning("No executable complete-set gap", "Neither splitting and selling at bids nor buying at asks and merging produces a positive gap after entered costs.")
        except ValueError as exc:
            warning("Invalid quote book", str(exc))
        st.info("The 58¢ and 47¢ numbers must be simultaneous executable bids for the split-and-sell calculation. Last-trade prices, midpoint estimates, or asks do not establish an arbitrage.")
        st.caption("[Polymarket: Positions & Tokens](https://docs.polymarket.com/concepts/positions-tokens) · [Polymarket: current fee rules](https://docs.polymarket.com/trading/fees). Makers currently pay zero; taker fees apply in fee-enabled categories, while geopolitical markets are fee-free.")

    else:
        concept("Order-book benchmark", "Kalshi's Yes and No sides are complementary views of one event-contract book. A Yes bid at x implies a No ask at 1−x, and a No bid at y implies a Yes ask at 1−y.")
        c1, c2 = st.columns(2)
        yes_bid = c1.number_input("Best Yes bid ($)", 0.0, 1.0, 0.58, 0.01, key="kalshi_yes")
        no_bid = c2.number_input("Best No bid ($)", 0.0, 1.0, 0.37, 0.01, key="kalshi_no")
        book = kalshi_complementary_book(yes_bid, no_bid)
        st.markdown("#### Translate bids into complementary asks")
        calculation_table(
            [
                ("1. Observe the best Yes bid", f"Yes bid = {yes_bid:.3f}", f"A trader will pay {money(yes_bid)} for Yes"),
                ("2. Derive the No ask", f"1.000 − {yes_bid:.3f}", f"No ask = {money(book.no_ask)}"),
                ("3. Observe the best No bid", f"No bid = {no_bid:.3f}", f"A trader will pay {money(no_bid)} for No"),
                ("4. Derive the Yes ask", f"1.000 − {no_bid:.3f}", f"Yes ask = {money(book.yes_ask)}"),
                ("5. Add the two best bids", f"{yes_bid:.3f} + {no_bid:.3f}", f"{money(yes_bid+no_bid)}"),
                ("6. Compute the bid–ask spread", f"1.000 − ({yes_bid:.3f} + {no_bid:.3f})", f"{money(book.spread)}"),
                ("7. Cost of buying both outcomes", f"{book.yes_ask:.3f} + {book.no_ask:.3f}", f"{money(book.yes_ask+book.no_ask)}"),
                ("8. Compare with settlement", f"1.000 − {book.yes_ask+book.no_ask:.3f}", f"{money(1-book.yes_ask-book.no_ask)} before fees; the loss equals the spread"),
            ]
        )
        if book.crossed:
            warning("Crossed inputs", "These two bids sum to more than $1 and should match rather than remain as independent executable best bids. A displayed 58¢ Yes trade and 47¢ No trade may refer to different times or quote sides.")
        elif abs(book.spread) < 1e-10:
            success("Locked book", "The opposing bids exactly fund the $1 contract and leave no bid–ask spread before fees.")
        else:
            concept("Normal order book", "The difference between $1 and the two best bids is the spread. Buying both sides means paying the derived asks, so the pair costs more than $1 by that same spread—not an arbitrage.")
        st.caption("[Kalshi: order-book complementarity](https://docs.kalshi.com/getting_started/orderbook_responses) · [Kalshi: settlement](https://docs.kalshi.com/getting_started/market_settlement). Kalshi charges transaction fees under its current fee schedule; simple Yes/No settlement itself has zero settlement fee.")

    st.markdown("---")
    st.markdown("**The durable lesson:** the terminal identity Yes + No = $1 is universal for a correctly specified binary claim. The date-0 trading relation depends on funding, collateral, quote side, execution, fees, and the platform's contract-creation mechanism.")


elif page == "4 · Price and belief":
    st.title("4 · Price and belief")
    hero("A price can look like a probability without being your forecast", "The correct normalization depends on the market mechanism; a physical belief still answers a different question.")
    interpretation = st.radio("Institutional setting", ["Polymarket", "Kalshi", "General derivative theory"], horizontal=True)
    convention = "discounted" if interpretation.startswith("General") else "full_collateral"
    c1, c2, c3, c4 = st.columns(4)
    price = c1.slider("Yes price ($)", 0.01, 0.99, 0.44, 0.01)
    maturity = c2.slider("Maturity (years)", 0.05, 5.0, 0.5, 0.05)
    rate = c3.slider("Continuous rate (%)", -5.0, 20.0, 4.0, 0.25) / 100
    belief = c4.slider("Your physical belief (%)", 0, 100, 55) / 100
    q = implied_probability(price, rate, maturity, convention)
    expected = expected_profit(belief, "yes", price)
    a, b, c = st.columns(3)
    a.metric("Discount factor", f"{discount_factor(rate, maturity):.4f}")
    b.metric("Normalized price", f"{q:.1%}")
    c.metric("Subjective expected profit", money(expected))
    if convention == "discounted":
        st.latex(r"P_{Yes}=P(0,T)\,q^{*}(Yes)\quad\Rightarrow\quad q^{*}(Yes)=P_{Yes}/P(0,T)")
    else:
        st.latex(r"P_{Yes}+P_{No}=1\quad\text{and the quoted Yes price is commonly read directly on a 0--1 scale}")
        if interpretation == "Polymarket":
            st.caption("On Polymarket, that scale is tied to fully collateralized outcome tokens and the $1 split/merge convention.")
        else:
            st.caption("On Kalshi, that scale is tied to complementary Yes/No event-contract positions in a single order book.")
        st.caption("In either case, the 0–1 quote does not prove that price equals a true physical probability.")
    if q > 1:
        warning("Bound check", "The entered price exceeds the present value of its maximum $1 payoff under this simplified benchmark.")
    elif expected > 0:
        concept("Interpretation", "Your stated physical belief makes the purchase attractive in expectation, but the contract can still lose its full price. This is speculation, not arbitrage.")
    else:
        concept("Interpretation", "Under your stated physical belief, the expected payoff does not cover the purchase price. This remains a belief-based comparison, not a replication result.")
    why("Separating physical belief from risk-adjusted pricing prevents the common mistake of treating every market price as an unbiased forecast.")


elif page == "5 · Multi-outcome markets":
    st.title("5 · Multi-outcome markets")
    hero("One—and only one—state must pay", "For mutually exclusive and exhaustive outcomes, buying every state claim reproduces a $1 payoff.")
    names = ["Orcas", "Comets", "Falcons", "Voyagers"]
    defaults = [0.31, 0.28, 0.24, 0.20]
    cols = st.columns(4)
    prices = [cols[i].number_input(f"{name} price ($)", 0.0, 1.5, defaults[i], 0.01, key=f"multi_{i}") for i, name in enumerate(names)]
    convention_label = st.radio("Complete-set convention", ["Fully collateralized platform", "General derivative theory"], horizontal=True)
    convention = "full_collateral" if convention_label.startswith("Fully") else "discounted"
    c1, c2 = st.columns(2)
    maturity = c1.number_input("Settlement horizon (years)", 0.0, 10.0, 0.25, 0.25)
    rate = c2.number_input("Continuous rate (%)", -10.0, 30.0, 0.0, 0.25) / 100
    gap = complete_market_gap(prices, rate, maturity, convention)
    table = pd.DataFrame({"Outcome": names, "Claim price ($)": prices, "Payoff if that outcome occurs ($)": [1.0] * 4})
    st.dataframe(table, hide_index=True, width="stretch")
    a, b, c = st.columns(3)
    a.metric("Package price", money(sum(prices)))
    b.metric("Complete-set benchmark", money(complete_set_benchmark(rate, maturity, convention)))
    c.metric("Package gap", money(gap))
    st.info("The parity conclusion requires the listed outcomes to be both mutually exclusive and exhaustive. ‘Other team wins’ or ‘tournament cancelled’ can be economically important omitted states.")


elif page == "6 · Practice-token market maker":
    st.title("6 · Practice-token market maker")
    hero("See price impact, not a betting recommendation", "Trade fictional outcome claims against an automated market maker and watch information-like prices respond to order flow.")
    outcomes = ["Orcas", "Comets", "Falcons", "Voyagers"]
    liquidity = st.slider("Liquidity parameter b", 2.0, 50.0, 12.0, 1.0, help="A larger b means the same trade moves prices less.")
    current = outcome_prices(st.session_state.lmsr_q, liquidity)
    price_df = pd.DataFrame({"Fictional outcome": outcomes, "Displayed price": current, "Market shares outstanding": st.session_state.lmsr_q})
    st.dataframe(price_df.style.format({"Displayed price": "{:.1%}", "Market shares outstanding": "{:.1f}"}), hide_index=True, width="stretch")
    c1, c2, c3 = st.columns([1.4, 1, 1])
    selected = c1.selectbox("Outcome to trade", outcomes)
    shares = c2.number_input("Shares (+ buy, − sell)", -20.0, 20.0, 3.0, 1.0)
    c3.metric("Practice-token cash", f"{st.session_state.lmsr_cash:.2f}")
    quoted, after_q, after_prices = trade_cost(st.session_state.lmsr_q, outcomes.index(selected), shares, liquidity)
    st.caption(f"Preview: this order changes practice-token cash by {quoted:.3f}; {selected}'s displayed price moves from {current[outcomes.index(selected)]:.1%} to {after_prices[outcomes.index(selected)]:.1%}.")
    buy_col, reset_col = st.columns(2)
    if buy_col.button("Execute practice-token trade", type="primary", width="stretch"):
        if quoted > st.session_state.lmsr_cash:
            warning("Insufficient practice tokens", "Reduce the order size or reset the simulation.")
        else:
            st.session_state.lmsr_q = after_q
            st.session_state.lmsr_cash -= quoted
            st.session_state.lmsr_log.append({"Outcome": selected, "Shares": shares, "Cost (+ paid / − received)": quoted})
            st.rerun()
    if reset_col.button("Reset market and practice tokens", width="stretch"):
        st.session_state.lmsr_q = np.zeros(4)
        st.session_state.lmsr_cash = 100.0
        st.session_state.lmsr_log = []
        st.rerun()
    if st.session_state.lmsr_log:
        st.dataframe(pd.DataFrame(st.session_state.lmsr_log), hide_index=True, width="stretch")
    concept("What the mechanism guarantees", "Displayed outcome prices are positive and sum to one. Buying an outcome raises its price; a larger liquidity parameter reduces price impact for the same order.")
    warning("What it does not guarantee", "A displayed price is not necessarily a true probability. Order flow can reflect information, hedging, noise, manipulation, wealth, or liquidity needs.")


elif page == "7 · Digital-option bridge":
    st.title("7 · Digital-option bridge")
    hero("Prediction claims are digital options", "Both depend on whether a threshold is crossed, but a standard call keeps gaining value beyond the strike.")
    strike = st.slider("Threshold or strike K", 20.0, 200.0, 100.0, 5.0)
    st.plotly_chart(style_plotly(digital_call_chart(strike)), key="digital_call_bridge", width="stretch", theme=None)
    left, right = st.columns(2)
    with left:
        concept("Digital claim", "Pays a fixed $1 if Sₜ > K and $0 otherwise. Its payoff has a jump at the threshold.")
    with right:
        concept("Standard call", "Pays max(Sₜ−K,0). Once in the money, its payoff has slope +1 rather than staying fixed.")
    st.info("The exact treatment of Sₜ = K is part of the contract definition. This studio uses a strict ‘greater than’ condition.")


elif page == "8 · Applied challenges":
    st.title("8 · Applied challenges")
    hero("Translate stories into contracts and trades", "Attempt each problem before opening progressively more informative hints or the complete reasoning.")
    titles = [item["title"] for item in CHALLENGES]
    index = st.selectbox("Choose a challenge", range(len(titles)), format_func=lambda i: f"{i+1}. {titles[i]}")
    item = CHALLENGES[index]
    st.subheader(item["title"])
    st.write(item["setting"])
    st.markdown(f"**Your task:** {item['prompt']}")
    response = st.text_area("Write your reasoning before requesting help", key=f"attempt_{index}", height=120)
    if st.button("Record my attempt", key=f"record_{index}"):
        if response.strip():
            st.session_state.challenge_attempted.add(index)
            success("Attempt recorded", "Now compare your reasoning with a hint or the complete explanation.")
        else:
            warning("Try first", "Write at least one sentence so that the hint responds to an actual attempt.")
    attempted = index in st.session_state.challenge_attempted
    with st.expander("Hint 1", expanded=False):
        st.write(item["hint1"] if attempted else "Record an attempt first.")
    with st.expander("Hint 2", expanded=False):
        st.write(item["hint2"] if attempted else "Record an attempt first.")
    with st.expander("Complete reasoning", expanded=False):
        st.write(item["solution"] if attempted else "Record an attempt first.")
    if st.button("Clear this attempt", key=f"clear_{index}"):
        st.session_state.challenge_attempted.discard(index)
        st.session_state.pop(f"attempt_{index}", None)
        st.rerun()


elif page == "9 · Knowledge check":
    st.title("9 · Knowledge check")
    hero("Check the distinctions that matter", "Questions and answer positions are shuffled for practice. Nothing is graded or transmitted.")
    order = list(range(len(QUESTIONS)))
    rng = np.random.default_rng(st.session_state.quiz_seed)
    rng.shuffle(order)
    score = 0
    answered = 0
    for display_number, question_index in enumerate(order, 1):
        prompt, _, correct, explanation = QUESTIONS[question_index]
        safe_prompt = prompt.replace("$", "&#36;")
        safe_explanation = explanation.replace("$", "USD ")
        st.markdown(f"**{display_number}. {safe_prompt}**")
        choices = shuffled_choices(question_index, st.session_state.quiz_seed)
        answer = st.radio("Choose one", ["— Select —"] + choices, key=f"quiz_{st.session_state.quiz_seed}_{question_index}", label_visibility="collapsed")
        if answer != "— Select —":
            answered += 1
            if answer == correct:
                score += 1
                st.success(f"Correct. {safe_explanation}")
            else:
                st.error(f"Not yet. {safe_explanation}")
        st.divider()
    st.metric("Current score", f"{score} / {answered}" if answered else "Not started")
    if st.button("Shuffle and retry", width="stretch"):
        st.session_state.quiz_seed = secrets.randbits(63)
        st.rerun()
