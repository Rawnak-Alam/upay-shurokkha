# User validation checklist

## Agent planning
- Open the app and confirm that all data is labelled synthetic.
- Cash shortage: inspect the recommendation, then reveal actual demand.
- Change to Float shortage; verify recommendation can move cash into float or choose no action.
- Change to High rebalance cost; verify no exchange is recommended.
- Set cash and float to zero; verify no positive-value request can be served.
- Try Unexpected cash-out surge; observe limitations rather than guaranteed service.
- Change service preference. Higher availability may cost more; expected net benefit is separate.
- Download a forecast and inspect its columns and values.

## Payment safety and review
- Ordinary family payment: low concern in the preset.
- Suspicious account request: high concern, with separate signals and reviewed-case assumption.
- Remove reviewed adverse cases and compare the score: the warning is evidence dependent.
- Legitimate large payment: may receive medium concern; it must not call anyone a scammer.
- Limited recipient information: insufficient information, not safe.
- Possible account takeover: device/recovery context should be visible.
- Edit a description: click Check payment again to update the displayed result.
- Continue is disabled until independent verification is checked.
- Request review and inspect the same case, evidence and customer action in Case Review.
- Review actions stay in this session; clear the cases and confirm removal.

## Evidence and reproducibility
- Read mistakes in held-out text. Note the very small sample size.
- Confirm mean earnings include exchange costs and show all baselines.
- Run tests, then evaluation. Re-running with the same environment should reproduce results.
- Check README, slides and report against artifacts/metrics.json.

## Final submission
- Add team name and both registered member names in submission.json.
- Test and push preserved commits; do not manufacture or backdate history.
- Deploy and add the real live URL in README and submission.json.
- Record a 5–6 minute video; test its viewing permissions while signed out.
- Run scripts/check_submission.py; verify the official portal fields and deadline.
- Upload files, submit, and save portal confirmation.
