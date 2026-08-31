# Prediction Market Studio v1.0

An ungraded Streamlit practice laboratory for binary and multi-outcome prediction contracts. All contracts and market data are hypothetical. The studio uses no live odds, money, accounts, student records, or grade transmission.

## Learning path

1. Contract anatomy and settlement rules
2. Payoff versus profit
3. Theory versus practice: textbook replication, Polymarket split/merge mechanics, and Kalshi's complementary order book
4. Market-implied risk-adjusted probability versus physical belief
5. Mutually exclusive and exhaustive multi-outcome claims
6. A practice-token LMSR automated market maker
7. The digital-option bridge
8. Eleven attempt-first applied challenges
9. Twenty-three shuffled knowledge-check questions

## Run locally

From this folder:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8790
```

On Windows, `Launch Prediction Market Studio.cmd` performs the launch step.

## Test

```powershell
python -m pytest -q
```

## Streamlit Community Cloud

Push this complete folder to the course repository. When creating the app, choose the repository and branch, then set the main file path to:

`chapter_04_option_basics/studio/Prediction_Market_Studio_v1.0/app.py`

If this folder is instead used as the root of a standalone repository, set the main file path to `app.py`. No secrets are required. After deployment, copy the public app URL into the LMS/Canvas page as an external link that opens in a new tab.

## File organization

- `app.py`: student interface and learning flow
- `prediction_engine.py`: payoff, profit, discounting, parity, and digital-option calculations
- `market_maker.py`: LMSR price and trade-cost calculations
- `challenge_bank.py`: applied attempt-first problems and hints
- `question_bank.py`: shuffled knowledge check
- `ui.py`: shared visual styling
- `tests/`: numerical and content checks

## Institutional sources and model boundaries

The platform comparison is based on the official [Polymarket positions and tokens](https://docs.polymarket.com/concepts/positions-tokens), [Polymarket fees](https://docs.polymarket.com/trading/fees), [Kalshi order-book](https://docs.kalshi.com/getting_started/orderbook_responses), and [Kalshi settlement](https://docs.kalshi.com/getting_started/market_settlement) documentation. Platform rules and fees can change, so current rules should be rechecked before reuse.

The exercises explicitly distinguish bids, asks, last prices, collateral funding, and execution. They still abstract from counterparty/default risk, taxes, latency, and detailed account-level rules. The automated market maker illustrates price impact mechanically; it does not establish that prices are true probabilities or encourage real-money trading.
