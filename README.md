# Upay Shurokkha

**Safer payments and smarter agent liquidity.** An independent AI Hackathon 2026 prototype for DIU CPC × upay. All data, recipients and financial outcomes are synthetic. No affiliation, production integration or real money movement is claimed.

Primary track: **05 — Merchant & Agent Intelligence**. Supporting capability: **01 — Trust & Risk Intelligence**.

## Live deployment

**Not deployed yet.** Before submission, replace this sentence with the verified public app URL and enter it in `submission.json`. The code is ready for Streamlit Community Cloud; deployment requires the repository owner's account. Do not submit with this field unfinished.

Repository: https://github.com/Rawnak-Alam/upay-shurokkha

## Problem and product

Agents can have enough total working capital but insufficient physical cash for cash-out or insufficient electronic float for cash-in. Our planner forecasts both demand streams and compares affordable exchanges against doing nothing. Customers can also be manipulated into sending money: the payment check combines optional Bangla/Banglish/English context with explicit account signals and gives a concern index, explanations and a simulated customer choice.

The index is **not a calibrated fraud probability** and does not determine whether a recipient is a scammer. A low score never guarantees safety. Limited history has a separate status.

## Judge-facing demonstration

Two short flows are visible by default. Agent Planning shows a fictional agent's counted cash, demo wallet float, demand forecast, suggested exchange and three plain-language reasons. Payment Safety shows a fictional recipient, amount, optional customer explanation, concern index, evidence sources and independent verification. Case Review and Evidence & Guide hold technical detail.

The [public upay Agent listing](https://play.google.com/store/apps/details?id=bd.com.upay.agent) describes a dashboard, real-time statement, item-wise transactions and instant commission. Those are the feature references for the agent concept. We do not claim knowledge of its private data schema, rates, balance API or actual forecasting inputs. All transaction and recipient histories here are synthetic. Physical cash is entered by the demonstrator; wallet float is a fictional sample. The payment flow uses no complaint registry, device telemetry or verified recipient risk profile.

The concern index is an **uncalibrated design score**, not a probability or verdict. The hospital example can trigger a warning despite being legitimate. Judges can see why it appeared. The agent exchange suggestion assumes a partner is available and costs are illustrative.

## Implemented features

- Fictional agent scenarios with only two visible balance inputs, a recommended exchange and source-aware reasons.
- Hourly cash-in/out forecast and actual-day comparison under an optional replay.
- Pre-payment examples with amount and optional English, Bangla or Banglish reason.
- Clear distinction between entered information, synthetic historical data and unavailable provider evidence.
- Simulated cancel, reviewer request and confirmed continuation; no real transfer.
- Reproducible time-split and held-out-scenario evaluation under Evidence & Guide.

## Technology and requirements

Python 3.12 recommended; tested here on Python 3.12 Linux. Windows CMD launchers are included. Ordinary CPU laptop; no GPU, production data, paid AI service or API key required. Internet is needed for initial package installation and deployment. Runtime inference works without an external API.

Streamlit, Plotly, pandas, NumPy and scikit-learn. Extra Trees handles numerical demand forecasting. Character TF-IDF plus logistic regression handles payment descriptions. Business rules, balance accounting and recommendations are deterministic. Explanations are templates grounded in available inputs, not LLM-generated claims.

Exact tested package versions are in `requirements.txt`; developer/test dependencies are in `requirements-dev.txt`.

## Windows setup — Command Prompt

From your project folder:

```cmd
cd /d "F:\Hackathon Files\upay-shurokkha"
setup_windows.cmd
start_windows.cmd
```

The first script creates `.venv` and installs packages. The second starts the app. If the browser does not open, visit http://localhost:8501. Stop with Ctrl+C in the terminal. Keep that terminal open while using the app.

Manual alternative:

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

If Python is unavailable, install Python 3.12 and reopen CMD. If `python` opens the Microsoft Store but `py` works, use `py -3.12 -m venv .venv` for the first line.

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

## Environment and configuration

No environment variables or secrets are required. UI theme lives in `.streamlit/config.toml`. Numerical defaults are in `shurokkha/liquidity.py`; synthetic assumptions are in `docs/MODEL_CARD.md`. Team/link fields are in `submission.json`. No production authentication is implemented; deploy only with synthetic examples.

## Test and reproduce

Windows CMD:

```cmd
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\evaluate.py
.venv\Scripts\python.exe scripts\check_submission.py
```

Other platforms: use `python` instead of `.venv\Scripts\python.exe`. Evaluation writes `artifacts/metrics.json`, CSV results and both synthetic datasets. The app retrains the small models at first launch and caches them in memory. There is no serialized model to download. No frontend build step is required.

Submission checking intentionally fails until your team and live/video URLs are supplied. It does not verify link accessibility.

## Measured prototype results

All figures below describe one seeded simulation, not upay performance.

| Measure | Baseline | ML approach |
|---|---:|---:|
| Hourly cash-in MAE (BDT) | 1,466.07 | 1,209.83 |
| Hourly cash-out MAE (BDT) | 2,274.67 | 1,613.86 |
| Mean net earnings / agent-day (BDT) | 328.89 historical forecast + optimizer | 339.88 |
| Mean refused requests / agent-day | 7.92 historical forecast + optimizer | 5.06 |

No-rebalance mean net earnings were **334.65 BDT**, so improvement over doing nothing was only **5.22 BDT per agent-day**. ML beat historical forecasting in 24 of 63 days, lost in four, and tied in 35. Lower forecast error does not guarantee higher earnings every day. Two planned ML actions became infeasible under realized demand and were skipped.

Text holdout: 24 sentences from unseen scenario families. Model: TP 11, FP 2, FN 1, TN 10; precision 84.6%, recall 91.7%, false-warning rate 16.7%. Keyword baseline: TP 3, FP 3, FN 9, TN 9. These are text-classifier results, **not a validation of the full concern score**. Eight sentences per language are too few to establish fairness or real-world accuracy.

## How AI is evaluated

Demand: 154 days × three agents × 12 hourly bins. Lag features use previous days at the same hour; all input features exist before opening. First 14 days provide lags. Train ends April 22, validation spans April 23–May 13, test spans May 14–June 3, 2026 (simulated dates). No test refitting. Baseline averages the same hour seven and 14 days earlier. Compare both forecasts through the same optimizer and arrival sequences on 63 agent-days.

Safety: manually authored 28 scenario families × three languages = 84 sentences, split by family: 48 train, 12 validation, 24 test. Threshold is selected on validation only. Templates are a tiny feasibility dataset, not representative prevalence. Train/test scenario families differ but may share ordinary phrases and scam concepts.

## Economics and limits

Illustrative commission: 0.4% of served value. Exchange cost: 25 BDT + 0.1% of exchanged amount. Exchange capacity: 20,000 BDT. Default capital: cash 6,000 + float 24,000 BDT. Rates are invented assumptions, not upay commission rates. Costs and commissions use a separate operating ledger; they do not instantly change wallet balances. No financing, rent or travel delay is included.

The optimizer searches a finite grid; it does not guarantee a global optimum. Rebalancing requires a partner assumed available. Production history may omit refused demand. Correlated shocks, varied arrival order, missing data, new agents and real language variation require further validation. No user interviews or real-world pilot were conducted for this prototype.

See [model card](docs/MODEL_CARD.md), [validation checklist](docs/VALIDATION.md), [demo script](docs/DEMO_SCRIPT.md), [deployment guide](docs/DEPLOYMENT.md), [report](docs/Project_Report.pdf) and [slides](docs/Presentation.pptx).

## Architecture

- `shurokkha/data.py`: reproducible requested-demand generator and within-hour tickets.
- `shurokkha/forecast.py`: time-safe features, model and baseline, calibration split.
- `shurokkha/liquidity.py`: balance ledger, feasible exchanges and expected utility.
- `shurokkha/safety.py`: multilingual classifier and explicit concern policy.
- `app.py`: interactive experiences and session-only review actions.
- `scripts/evaluate.py`: offline reproducibility and evidence generation.
- `tests/`: accounting, no-future-data and end-to-end interaction tests.

The core functions can be wrapped in an authenticated API later. There is no implemented production API or upay integration in this version.

## Phase 2 extension points

Replace data adapters; change commission/capital constraints; add partner capacity or rebalancing delay; update forecasts intraday; modify risk weights and review rules. Prioritize the actual on-site requirements. Record new changes in genuine commits; do not backdate history.

## External resources and AI assistance

Open-source dependencies are listed above. Code and drafts were developed with OpenAI Codex assistance during this workflow. Synthetic demand and hand-written text examples were created for this prototype; no external customer dataset, paid model API or pretrained language model is used. Team members must review, understand, validate and be able to explain the submitted work. Development commits preserve the assistant identity rather than impersonating team members.

Reference materials: AI Hackathon 2026 Student Project Guideline (DIU CPC × upay) and AI DEV FEST 2026 Official Rulebook supplied by the user. Deployment guidance: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## License

MIT, as already selected in this repository. See `LICENSE`. Third-party packages retain their own licenses. The bundled Noto Sans Bengali font is from google/fonts and uses the SIL Open Font License in assets/FONT_LICENSE.txt. The upay name does not imply endorsement.
