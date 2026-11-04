# Submission checklist — due Tue Nov 3, 2026, 23:59 PT

Status: **everything complete and verified.** Nothing is left unticked. The single submit step is below — copy the URL, paste it as the website-URL submission in Canvas, done.

## Submit step (the only action left)

- [x] Canvas submission ready: paste **https://pranith27.github.io/data-mining-methodologies/** as the website-URL submission in Canvas before Nov 3, 2026, 23:59 PT. Everything it points to is finished and verified — this paste is the submission itself.

## Repo checklist — all done

- [x] Project folder complete: `data-mining-methodologies/` with 3 methodology projects
- [x] Public repo created: https://github.com/pranith27/data-mining-methodologies
- [x] All files pushed to `main`
- [x] Colab links wired to pranith27 in all 3 project READMEs
- [x] GitHub Pages enabled from `main` branch, root folder
- [x] Submission site live and checked: https://pranith27.github.io/data-mining-methodologies/ (HTTP 200)
- [x] Every project link on the site clicked and verified; all `index.html` links resolve
- [x] All 3 notebooks execute clean, 0 error cells: CRISP-DM 23 cells, SEMMA 24 cells, KDD 31 cells
- [x] All metrics in reports/articles cross-checked against executed notebook output
- [x] KDD final-model fix confirmed: deployment cell refits with tuned hyperparameters (`max_depth=10`), giving good-profile 6.89 / faulty-profile 4.56, matching the report
- [x] 3-round critic revision logs complete for every project (`critic-revisions.md`)

## Published work — all live

- [x] 3 Medium articles published and linked in the main README and on the site:
  - CRISP-DM: https://medium.com/@pranithvarma.234/we-lost-1-in-4-customers-heres-what-the-data-said-and-what-we-did-about-it-440560d129bb (verified live)
  - SEMMA: https://medium.com/@pranithvarma.234/i-ran-a-1980s-heart-dataset-through-semma-and-the-models-tied-259cc51eb0dd (verified live)
  - KDD: https://medium.com/@pranithvarma.234/what-1-599-wines-taught-me-about-quality-a-kdd-story-3b7e54325f24
- [x] 3 YouTube walkthroughs public and verified (oEmbed 200), linked in the main README and on the site:
  - CRISP-DM: https://youtu.be/A_KGWct-lUg · SEMMA: https://youtu.be/srAwSKYl9YM · KDD: https://youtu.be/fTEAhjRz0nE
- [x] Draft/source files removed from the repo (`medium-article.md`, `video-script.md`, `walkthrough.mp4`) — the published URLs are the deliverables now

## Deployment artifacts — all three projects

- [x] CRISP-DM: `01-crisp-dm-telco-churn/artifacts/best_model.pkl` (Logistic Regression pipeline)
- [x] SEMMA: `02-semma-heart-disease/artifacts/best_model.pkl` — tuned Random Forest (n_estimators=200, max_depth=8, min_samples_leaf=2), reproduction sanity-checked against the notebook (test ROC-AUC 0.9610 = executed 0.961)
- [x] KDD: `03-kdd-wine-quality/artifacts/best_model.pkl` — tuned Random Forest regressor (n_estimators=500, max_depth=10, min_samples_leaf=5), reproduction sanity-checked (R² 0.4298, RMSE 0.6373 = executed values)
- [x] Every artifact has a `MODEL_CARD.txt` (model, training data, usage) and a `build_final_model.py` reproducer script
- [x] All three `.pkl` files load and predict correctly (verified)

## Reproducibility fixes

- [x] SEMMA notebook figure saves fixed to `figures/` (5 charts) with `os.makedirs("figures", exist_ok=True)` — reruns now update the repo's stored figures
- [x] All `requirements.txt` files pin exact versions (pandas==2.1.4, numpy==1.26.4, scikit-learn==1.9.1, matplotlib==3.6.3, seaborn==0.13.2, nbformat==5.9.1)
