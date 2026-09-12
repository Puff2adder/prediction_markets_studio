# Prediction Studio: teaching guide

Begin on Start here, which describes the studio without a computation. Each teaching page presents a problem, what students will learn, defined default data, and a worked analysis. Sensitivity controls are initially hidden and appear after the explanation. Changing them leaves the worked benchmark unchanged. Consolidation questions and an accomplishment statement conclude each case.

Suggested 30-minute sequence:
- Introduction and sports payoffs: 4 minutes. A Yes claim pays one dollar on a Harbor win; draws belong to No. Separate payout from financed profit.
- Complete sets: 7 minutes. First replicate the binary pair, then choose three outcomes. Emphasize disjoint and exhaustive events and replication of home-or-draw.
- Prices and beliefs: 7 minutes. At zero interest, 100 claims priced at $0.62 cost $62. A 70% personal win belief gives expected profit $8, with an actual loss of $62 still possible. Personal belief, true physical probability, and the pricing probability are distinct concepts. The compact expression n(p−q) is terminal expected profit after financing for one-dollar claims; its present value is P(0,T)n(p−q).
- GDP protection: 8 minutes. Assume objective low-GDP probability 20%, a one-dollar claim price $0.30, and zero interest. Then q = 30%. Income is $60 or $100; 40 claims cost $12 and make net income $88 in either state. Expected claim profit is −$4. Protection transfers income into the state where an extra dollar is especially useful. This explains possible willingness to pay a premium; it does not derive an exact price from p or assert that the displayed insurance choice is universally optimal.
- Brief token conversion connection and wrap-up: 4 minutes. Immediate collateral differs from a payment-date bond. Use asks to buy, bids to sell, and subtract total costs. Quotes are invented; this is not a live opportunity.

For each exploration, ask for a prediction before opening the controls. In the belief example, change p with price fixed, then price with p fixed. In GDP, increase price with objective p fixed, then change p with price fixed. Ask which cash flows change and which expectations change. Twelve reusable MCQs and three short numerical questions provide further ungraded practice. Answers are available only after an attempt.

Assumptions are local: sports and beliefs start at zero interest; complete sets start at 4% continuously compounded for six months; GDP fixes zero interest over one year; token conversion is immediate. The GDP example uses dollar-denominated stylized income, not actual GDP or household data. No Kalshi or advanced pricing-kernel model is included in the student interface. Legacy engine utilities are retained for compatibility but are not used to derive the GDP price.

Deployment requires the new case_analysis.py module alongside app.py, engine.py, questions.py and studio_theme.py. Keep .streamlit/config.toml and requirements.txt in the standalone repository. Theme CSS and explicit chart styling supplement the light configuration.
