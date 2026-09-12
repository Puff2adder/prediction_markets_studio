# Delivery checks — 12 September 2026

77 automated tests pass under Python and Streamlit 1.51. Checks cover the financial engine, all seven pages, both complete-set choices, invalid quotes, all twelve MCQ answers, numeric attempts and solution disclosure, section reset, hidden sensitivity controls, and preservation of fixed benchmark data after scenario changes.

Headless Chrome rendered the introduction, five worked cases, all five sensitivity panels, and practice against the running app on port 8792. Screenshots were inspected for the home page, complete sets, prices/beliefs, GDP exploration and token conversion. A dollar-sign parsing issue in table cells was corrected and the browser checks and automated suite rerun successfully. The light configuration, contrast CSS, and explicit Plotly style remain included.

Benchmarks: sports cost 62 and terminal profit 38 or −62; belief-weighted expected profit 8 at p=.70, q=.62; binary complete-set value exp(−.02)=.9801986733 and arbitrage profit today .0401986733; GDP protection costs 12, equalizes net income at 88, and has expected claim profit −4 at p=.20; immediate buy/merge gain .02 after costs.

The previous deliverable is preserved in prediction_studio_before_guided_sequence.zip. The refreshed complete package includes case_analysis.py, all other application modules, requirements, theme configuration, launcher, tests and documentation. No GitHub upload or remote deployment was performed.

## Practice calculator update

88 automated tests pass, including arithmetic validation, all three calculator-to-answer transfers, invalid-expression handling and reset. Each calculator is available immediately without revealing a solution. calculator.py is now required for deployment and included in the complete ZIP.
