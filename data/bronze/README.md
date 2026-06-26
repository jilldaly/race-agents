# Bronze layer (raw, immutable, shared)

Drop raw results here:

```
data/bronze/<race>/<year>/results_<distance>.pdf
```

e.g. `data/bronze/cork/2026/results_full.pdf`. A `meta.yaml` with provenance is
written automatically when files arrive via `racedata`'s store. The actual PDFs
are gitignored — copy them in locally, or (Phase 5) let the scraper populate this
via the bronze store. In hosted deployments this layer lives in an object-store
bucket instead (`BRONZE_BACKEND=s3`).
