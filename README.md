---
title: Calculator_app
emoji: 📊
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.10.0
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Calculator app

Streamlit app that adds two slider values. The YAML block above is the Hugging Face Spaces configuration. The Space reads `sdk`, `sdk_version`, and `app_file` from that block when it builds. `sdk_version` stays `1.10.0` and `app_file` stays `app.py`.

`app.py` shows two sliders, 300.0–500.0 and 180.0–200.0, and writes the sum of the selected values. It imports `numpy` and `streamlit`. It has no model download, no external API call, and no data-file path.

## Local setup

Use Python 3.10. `requirements.txt` pins `streamlit==1.10.0` to the Spaces `sdk_version`, `numpy==1.23.5` (imported by `app.py`; wheels are published for Python 3.8–3.11), and `altair==4.2.2`. Streamlit 1.10.0 imports `altair.vegalite.v4`, and Altair 5 and later removed that module, so a fresh resolver that is allowed to pick current Altair cannot import Streamlit. Other libraries that Streamlit pulls in are still unpinned.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit serves the app on port 8501 unless you pass another port. No token or API key is required to run it locally.

## Checks

The automated checks compile `app.py` and read the slider bounds, the `value1 + value2` expression, the dependency pins, the Spaces front matter, and the sync workflow. They do not launch Streamlit.

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q app.py
python -m pytest
```

`requirements-dev.txt` is only for those checks. The Space installs `requirements.txt`.

CI also installs `requirements.txt` on Python 3.10 and runs `python app.py`, which executes the script without starting the Streamlit server.

## Deployment

A push to `main` on `BhaveshWadibhasme/HuggingFaceSpaces`, or a manual run of the sync workflow on that branch, force-pushes `main` to `https://huggingface.co/spaces/Bhavesh302/Calculator_app`. The force-push is the existing sync: the Space can contain Hub commits that are absent from this history. The job reads `HF_TOKEN` from Actions secrets and passes it in the push URL, the same command shape this repository already used. Actions masks that secret in logs. The checkout uses `contents: read` and does not persist the GitHub token. Pull requests and forks are not synced. This repository does not publish a package.

The CI workflow runs the checks on pull requests and on `main`. It is separate from the sync workflow, so a failing check does not by itself stop a push that already reached `main` from syncing.
