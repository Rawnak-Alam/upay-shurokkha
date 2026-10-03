# Upay Shurokkha - agreed implementation

Primary track: 05 Merchant & Agent Intelligence. Supporting track: 01 Trust & Risk Intelligence.

1. Agent planning: forecast hourly requested cash-in/out, replay balances, recommend a feasible single cash/float exchange, compare economics with baselines.
2. Payment safety: combine a trained text classifier and transaction context into a disclosed concern index. Provide explanations and simulated customer/reviewer actions.
3. Evidence: chronological forecasting holdout, scenario-family text holdout, false warnings and shortcomings.

Synthetic data only. No live payments, production wallet connection, real customer lookup, or recipient guilt determination. No API keys or GPU required.

A concern index is not a calibrated fraud probability. Rebalancing exchanges balances and does not create working capital. Costs and commission are accounted in a separate operating ledger. All economics are assumptions, not upay rates.

Development commits are created as features become ready, using the configured Codex identity. The user reviews locally and pushes the preserved history. Team identity, live URL, and recorded video remain user-supplied submission items.
