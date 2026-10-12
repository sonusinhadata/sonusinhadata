# Setup

1. Copy everything in this folder into your `sonusinhadata` repo. Overwrite the old README.
2. DELETE the old One-Punch files from the repo: everything in `assets/` except the 3 new files,
   plus `source-photo.png`, `scripts/generate_ascii.py`.
3. Edit the CONFIG block in `scripts/generate_assets.py` (name, tiles, workflow), then:
       python scripts/generate_assets.py
       python scripts/update_readme.py
4. Commit and push. Check the profile in a private window.
Day to day: edit `data/progress.json`, push, and the README updates (GitHub Action; needs
Settings > Actions > General > Workflow permissions > Read and write).
