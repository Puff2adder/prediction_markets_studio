# Prediction Studio

A new, simplified Streamlit practice laboratory aligned with `prediction_version3_reviewed.tex` and the three-question digital-claims homework. The original studio remains separate. All examples are hypothetical and ungraded; the application makes no live-market calls, requests no student information and transmits no grades.

## Student sequence

0. **Start here:** a short description of the studio, with no calculations or input controls.
1. **Sports payoffs:** Harbor FC versus Valley United; Yes means Harbor wins in regulation, No includes draw or loss. Study the default payoff table before changing the purchase price and number of claims. Separate payoff, cost and financed profit.
2. **Complete sets:** binary Yes/No replication, borrowing/lending, then home win/draw/away win. Combine home and draw claims to replicate “Harbor does not lose”; distinguish overlapping events from a complete set.
3. **Prices and beliefs:** change a personal belief while holding the quote fixed. The expected-profit graph shows why disagreement is not arbitrage.
4. **GDP protection:** compare an assumed objective probability with a separately entered hypothetical market price. Explain the value of money in bad times using household income before and after protection. No advanced pricing model is used.
5. **Polymarket connection:** one brief hypothetical binary conversion example using bids, asks and total costs. Current collateral is distinguished from a future dollar.
6. **Practice:** the three short homework calculations and twelve multiple-choice questions with attempt-first feedback, hints, worked explanations and reset controls.

Each teaching case follows: problem → learning objectives → defined default data → worked analysis and outcome → optional sensitivity controls → consolidation questions → accomplishments. The fixed benchmark stays visible and unchanged when students alter the separate scenario. Prices and beliefs and GDP include a short sensitivity preview before the controls. Practice is attempt-first, with an optional worked benchmark.

Reset this section restores local defaults; Start over clears the session. All displayed inputs have local definitions and units. No advanced GDP pricing model is introduced: objective probability and the hypothetical insurance price are separate inputs.

## Run on Windows

Open a terminal in this folder:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8792
```

After installing requirements once, double-click **Launch Prediction Studio.cmd**. Open http://localhost:8792 if your browser does not open automatically. Port 8792 keeps this version separate from the older studio. For a separate environment, first run `python -m venv .venv`, then `.venv\Scripts\Activate.ps1`.

## Upload to GitHub and Streamlit Community Cloud

The easiest deployment is a separate repository, for example `prediction-studio-v2`, with the **contents of this folder at the repository root**. Upload `app.py`, **`calculator.py`**, **`case_analysis.py`**, `engine.py`, `questions.py`, `studio_theme.py`, `requirements.txt`, and `.streamlit/config.toml`. Include the README, launcher and tests if desired. Do not upload `__pycache__`, `.pytest_cache`, `.venv` or any secrets. A ZIP is a transfer package: extract it before uploading the files.

If GitHub's file chooser does not include the hidden configuration folder, choose **Add file → Create new file**, enter `.streamlit/config.toml` as the filename, paste the contents of the supplied file, and commit. The folder is created by the slash in that filename. Use Create new file, not Upload files, for this step.

In Streamlit Community Cloud, create an app from the repository and branch. Set the main file to `app.py`; use Python 3.11 or 3.12. Dependencies are in `requirements.txt`. No secrets are needed. Later commits to the deployed branch trigger an update; inspect Cloud logs if it fails. Copy the published URL into Canvas as an external link that opens in a new tab.

For the full course repository instead, the entry point is `chapter_04_option_basics/studio/Prediction_Market_Studio_v2.0/app.py`. Streamlit configuration is read relative to the launch working directory: put the supplied theme configuration in the repository-root `.streamlit/config.toml` when launching from the repository root. Review any existing root configuration before changing it. The app also applies contrast CSS and explicit Plotly colors, so text/graph contrast is not left to an inherited browser theme.

## Verification

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover state-price normalization, payoff replication in every outcome, financed P&L, the GDP comparative statics, insurance costs, conversion directions, input validation, all seven pages and the five optional sensitivity panels, both complete-set modes, all MCQs, hint/retry behavior and reset controls. See `QA_REPORT.md` for the delivery checks.

## Model boundaries and sources

The textbook sections assume a common payment date/currency, certain contractual settlement, no transaction costs and feasible borrowing, lending and shorting. All contracts pay $1 in the named outcome and zero otherwise. Interest is continuously compounded. The GDP price is a hypothetical input, not derived from the objective probability. The economic discussion explains a possible protection premium without imposing a pricing model. No actual GDP forecast, release date, exchange specification or sports odds are used.

The sports event is a guaranteed completed regulation-time match; real cancellation/void rules require additional states. The GDP example uses a specified hypothetical first annual real-growth release, g < 1% versus g ≥ 1%, with observation and payment at T. Slider changes to T describe alternative payment horizons, not actual match scheduling or publication calendars.

The platform illustration uses documented binary split/merge rights, with invented quotes and costs, successful execution and conversion, and no rewards or collateral risk. It is not a live trading opportunity. Official documentation checked 11 September 2026:
- https://docs.polymarket.com/concepts/positions-tokens
- https://docs.polymarket.com/trading/fees

## Files

- `app.py`: student interface and learning sequence.
- `engine.py`: pure financial calculations.
- `questions.py`: twelve conceptual questions and explanations.
- `studio_theme.py` and `.streamlit/config.toml`: paired text/background colors.
- `requirements.txt`, `requirements-dev.txt`: application and test dependencies.
- `tests/`: numerical and Streamlit interaction checks.
- `INSTRUCTOR_GUIDE.md`: model interpretation and suggested use.

Each numerical practice problem has a calculator available before an attempt. Students enter arithmetic (including exp for discounting), press Calculate, and optionally use the result as their answer. Checking the answer is a separate action.
