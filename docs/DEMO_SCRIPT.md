# Demonstration script — target 5 minutes 40 seconds

Rehearse with the running application. Record your own screen and narration. Keep the video at least five minutes if the submission interface still specifies that minimum. Replace any team introduction with your registered details. Do not present synthetic outcomes as a pilot.

## 0:00–0:40 | Problem and scope

"Our project is Upay Shurokkha. We help agents decide how much physical cash and electronic float they need, and help customers review warning signs before a payment. An agent can have enough total capital but the wrong balance to serve the next customer. Meanwhile a customer may be pressured into sending money. We built an interactive prototype with two decision flows. All data shown today is synthetic, and no money moves."

## 0:40–1:25 | Agent overview

Open Agent Planning. Select Campus gate, the last replay day, and Cash shortage. Keep Lower cost selected.

"Here we begin with six thousand taka in physical cash and twenty-four thousand in electronic float. Cash-in increases the agent's cash but consumes float. Cash-out consumes cash and adds float. Our model predicts both streams by hour from prior observations and calendar features. The shaded ranges come from errors on a separate validation period. They are estimates, not guarantees."

Point to the recommendation and read its actual amount and time from the screen.

## 1:25–2:10 | Recommendation and stress test

"The optimizer compares feasible exchanges, including doing nothing. It accounts for assumed commission and exchange costs. The suggested action converts one balance into the other; it cannot create capital."

Reveal actual synthetic outcomes. Read the values shown, including any loss or missed demand. Change to High rebalance cost.

"When the action costs too much, the system keeps the current balances. With Low capital, some demand remains unserved. This is why a forecast alone is not enough: the recommendation must respect real constraints."

## 2:10–3:05 | Payment safety

Open Payment Safety, choose Suspicious account request, click Check payment.

"This fictional customer was told to pay immediately to reactivate an account. Our description model adds a language signal. The policy also considers a first-time recipient, unusual amount and the synthetic reviewed-case evidence shown here. The score is a concern index out of one hundred; it is not a percentage chance that this recipient is a criminal."

Point to the reasons and Bangla guidance. Click Request human review. Then show Limited recipient information and run a new check.

"Missing history gives insufficient information. It must not be interpreted as proof of safety or guilt. The prototype requires confirmation before a simulated continuation."

## 3:05–3:35 | Reviewer

Open Case Review and select the first suspicious case.

"The reviewer sees the same input evidence, score contributions and customer action. They can request more evidence or escalate. Nothing here automatically blocks an account or sends an external complaint. Production would need authentication, audit logs and approved review procedures."

## 3:35–4:35 | AI and evaluation

Open Evidence & Guide.

"Forecasting uses Extra Trees, compared with the average of the same hour one and two weeks earlier. Evaluation is chronological: the last twenty-one days remain unseen during fitting. Across sixty-three synthetic agent-days, the ML strategy averaged about 340 taka net commission after exchange costs, versus 329 for historical forecasting and 335 for no action. The gain over doing nothing is about five taka per day in this simulation; it does not win every day."

"The language component is character TF-IDF plus logistic regression, trained from scratch. We held out scenario families so translations of a training example do not enter the test. On only twenty-four test sentences it found eleven of twelve scam examples and falsely warned on two of twelve legitimate examples. That dataset is too small to establish production accuracy. The full concern index is not calibrated."

## 4:35–5:20 | Limits and future pilot

"Our demand generator assumes calendar patterns and synthetic shocks. Real transaction histories may omit customers turned away, so a pilot should capture refused demand. The optimizer assumes an available exchange partner and no travel delay. The language model can miss paraphrases or misread quoted scam messages. We show these limits and mistakes."

"For a controlled pilot, we propose shadow predictions using governed data, followed by human-approved recommendations. We would measure served requests, full net costs, false warnings, reviewer effort and customer understanding."

## 5:20–5:40 | Reproducibility and Phase 2

Show the repository and README, then the final slide.

"The repository includes the generator, models, policy rules, tests and evaluation commands. We disclose AI-assisted development. The modules are separate so we can adapt costs, capital constraints, data sources or review rules to the organizers' Phase 2 requirements. Thank you."

## Before uploading

Check audio, readable text, the actual duration, and video access from a signed-out browser. Use the live app in the recording once deployed. Avoid reading personal account details or showing credentials.
