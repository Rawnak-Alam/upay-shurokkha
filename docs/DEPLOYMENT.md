# Deploy after local validation

1. Preserve and merge the supplied Git bundle into your existing clone using START_HERE.md in the delivery package.
2. Run the app and tests. Review code and submission files.
3. From your repository folder, run `git push origin main`. Use Git's browser sign-in if prompted.
4. Open https://share.streamlit.io and sign in with the GitHub account owning the repository.
5. Create an app from the existing repository. Repository: `Rawnak-Alam/upay-shurokkha`; branch: `main`; entrypoint: `app.py`.
6. In advanced settings, choose Python 3.12 if offered. No secrets are required. Deploy.
7. Open the actual assigned URL in a signed-out browser and on another device. Exercise both modules.
8. Put that exact URL in README's Live deployment section and `submission.json`. Add the recorded video's viewable URL and registered team details to `submission.json`.
9. Commit genuine reviewed changes and push. Run the local submission checker. Upload the report/slides and paste the links into the competition portal.
10. Save the actual portal confirmation. A working URL or local checker is not submission confirmation.

Official documentation checked for this workflow:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

If deployment fails, inspect its logs. Most relevant checks: correct main-file path; tracked requirements.txt and shurokkha package; compatible Python version; complete artifacts directory. The deployed app needs only requirements.txt, not report generation dependencies.
