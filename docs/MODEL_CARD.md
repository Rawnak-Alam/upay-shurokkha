# Model and simulation card

## Intended use

Synthetic hackathon demonstration of agent cash/float planning and payment-context warnings. No production decisions, real recipient assessments or fraud probabilities.

## Demand generation

Seed 20261004; 154 days starting January 1, 2026; three fictional agent segments; 09:00–20:00. Lognormal daily and hourly noise, assumed morning cash-in and afternoon cash-out peaks, Friday/Saturday effect and beginning/end-of-month cash-out peaks. Seven percent of generated agent-days receive an unannounced afternoon shock. These assumptions are invented and not derived from upay observations. No real identifiers or locations are used. The shock label is excluded from prediction features.

Hourly requested volumes are split into synthetic tickets of 500–2500 BDT with a possible smaller remainder and shuffled within the hour. All strategies see identical tickets during evaluation. Aggregation and ticket size can materially affect shortages. Served and refused requests are observable in this simulator; production completed-transaction data may be censored.

## Forecast

ExtraTreesRegressor: 100 trees, minimum leaf size 8, max_features 0.9, random_state 42. Predicts both hourly demand streams. Features: hour, weekday, payday/weekend flags, elapsed day, agent code, and each stream's same-hour lags at one, seven and 14 days. Models train once; later forecasts may use observed earlier test-day histories, as a real rolling-origin daily forecast could. They never use the target day's outcomes.

Split: 3,528 training rows, 756 validation rows, 756 test rows. Validation estimates absolute-error radii and three demand multipliers (20th, 50th, 80th percentiles of observed/predicted combined demand). Hourly error radii are pooled across agents; no coverage guarantee, agent-specific calibration or simultaneous full-day interval is claimed. Test marginal coverage: 87.6% cash-in, 91.3% cash-out.

## Optimizer and accounting

One optional exchange before 09:00, 12:00 or 15:00. Positive cash_delta converts float into physical cash; negative does the reverse. Candidate grid spans ±min(capacity, total working capital), nine evenly spaced values plus feasible edge candidates. An action is considered only if affordable in every tested prediction scenario. Realized demand can still make a later action infeasible; the simulator skips it and logs failure with no fee.

Cash-in increases cash and reduces float equally. Cash-out does the reverse. Whole tickets are either served or refused. No borrowing, partial fulfilment or overdraft. Cash + float is conserved. Fees and commission are external operating-account entries. Assumed instant partner access, no travel downtime, no financing costs.

Objective = expected net commission minus service_weight × expected refused value. Weights are 0, 0.001, 0.004 for Lower cost, Balanced, Higher availability. This expresses willingness to sacrifice profit to serve requests; it is not extra commission. Published economic evaluation uses Lower cost. No action is always feasible and wins an objective tie.

Three scenarios scale both demand streams with validation multipliers and use different artificial within-hour orders. They do not span all independent cash-in/out shocks. Prediction scenarios and realized sequences are kept separate.

## Safety classifier and concern policy

Character TF-IDF ngrams 2–5 and logistic regression C=8. Trained from scratch on 48 authored sentences; 12 validation; 24 test. All translations of a family remain in its split. Threshold selection penalizes validation false warnings twice as much as misses. The final threshold is approximately 0.50.

The model output is not calibrated for production prevalence. For nonempty text, the language contribution is 60 × clip((output − 0.2)/(threshold − 0.2 + 0.25), 0, 1). First recipient adds 8; amount above 2× usual adds up to 12; recovery + new device adds 22 (only one adds 8); reviewed adverse cases add min(30,20+5n). Total is capped at 100. Medium begins at 35, high at 65. Missing recipient history produces Insufficient information when otherwise below medium. No reviews or identity badge deduct risk.

Weights are explicit product assumptions. A trained language component does not validate the composite index. Reviews in this prototype are predefined synthetic evidence fields; it does not verify complaints. The device/recovery signal is a rule, not a trained account-takeover model.

## Limitations and failures

Text test has only four scam and four legitimate sentences per language; estimates are highly unstable. Negation and quoted scam narratives cause false warnings. Banglish paraphrases can be missed. No fairness guarantee, dialect coverage, cross-provider visibility, real fraud prevalence or causal prevention evidence exists. Explanations expose observed signals, not proof of malicious intent.

No external model receives inputs. Case text persists only in the Streamlit session and optional user-downloaded JSON. No backend case database, authentication, access roles, rate limits or durable audit trail exists. Public hosting must use fictional inputs. Future APIs should validate inputs and distinguish model availability from risk decisions. No arbitrary user text is executed or used as a system instruction.

## Pilot proposal

With upay approval, begin in shadow mode using governed requested-demand data, refused-request logs and reviewed case outcomes. Compare against operational baselines and costs, monitor language and new-account errors, validate score calibration if probabilities are ever introduced, then test human-approved actions. Measure net commission after full costs, false warnings, missed cases, reviewer effort and customer understanding. No production deployment or access is promised.
