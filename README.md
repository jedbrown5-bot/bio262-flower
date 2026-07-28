# BIO262 Flower Dissection

An interactive teaching tool. A generic flower is drawn in 3D and randomised
each round, with games and reference tabs.

## Tabs
- **Peel and name** — name the outermost whorl and it peels away.
- **Label the parts** — match numbered leader-line callouts to the part names.
- **Count and describe** — merosity, symmetry and fusion, then check.
- **Inside the ovary** — a transverse section, locules and placentation.
- **Special cases** — Eucalyptus, Asteraceae, Banksia, Callistemon, Acacia.
- **Glossary** — every part, a diagram, and a link to the Wikipedia article.

The 3D flower rotates by dragging with the mouse. Scroll to zoom, double-click
to reset the view.

## Files
- `flower_dissection_app.py` — the Streamlit app (run this one).
- `flower_core.py` — flower model and randomiser.
- `flower3d.py` — the 3D flower (Plotly).
- `ovary_section.py` — the ovary cross-section.
- `glossary.py` — glossary terms and Wikipedia links.
- `special_cases.py` — the special-case taxa, diagrams and quizzes.
- `glossary_images/` — the diagrams used by the Glossary tab.
- `requirements.txt` — the Python packages.

## Run it on your own computer
```
pip install -r requirements.txt
streamlit run flower_dissection_app.py
```
It opens in your browser. Press Ctrl+C in the terminal to stop it.

## Put it online for students (Streamlit Community Cloud, free)
1. Create a GitHub account if you do not have one, at github.com.
2. Make a new repository and upload the whole contents of this folder, including
   the `glossary_images` folder. Do not upload the `_to_delete` folder.
3. Go to share.streamlit.io and sign in with GitHub.
4. Click **Create app**, choose your repository and branch, and set the main
   file path to `flower_dissection_app.py`. Click **Deploy**.
5. After a few minutes you get a public link like `https://yourname.streamlit.app`.
   Share that link with students. Any change you push to GitHub redeploys.

Community Cloud reads `requirements.txt` to install streamlit, plotly, numpy and
matplotlib. The default Python version is fine.
