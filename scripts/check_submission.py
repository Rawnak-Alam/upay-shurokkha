"""Checks local completeness. Does not certify organizer compliance or public URL access."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'submission.json').read_text())
missing=[]
for k in ('team_name','live_url','video_url'):
    if not m.get(k): missing.append(f'Fill {k} in submission.json')
for i,n in enumerate(m.get('members',[]),1):
    if not n: missing.append(f'Fill registered member {i}')
for k in ('live_url','video_url','repository_url'):
    if m.get(k) and not m[k].startswith('https://'): missing.append(f'{k} must be an HTTPS link')
for f in ('README.md','app.py','docs/Project_Report.pdf','docs/Presentation.pptx','artifacts/metrics.json'):
    if not (ROOT/f).exists(): missing.append(f'Missing {f}')
if m.get('live_url') and m['live_url'] not in (ROOT/'README.md').read_text(): missing.append('Add live_url to README.md')
if missing:
    print('STILL TO COMPLETE:\n'+'\n'.join('- '+x for x in missing))
else: print('Local fields/files complete. Independently test URLs in a signed-out browser and verify portal submission.')
sys.exit(bool(missing))
