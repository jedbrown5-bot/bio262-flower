"""
flower_dissection_app.py
------------------------
BIO262 flower dissection game, Streamlit version.

Run it with:

    pip install -r requirements.txt
    streamlit run flower_dissection_app.py

A generic teaching flower is shown as a real 3D bloom that the student spins
with the mouse (drag to rotate, scroll to zoom), randomised each round. Modes:

  - Peel and name   : name the outermost whorl and it peels away
  - Label the parts : match each numbered marker to the right part name
  - Count and describe : answer merosity, symmetry and fusion, then check

The flower model lives in flower_core.py; the 3D drawing lives in flower3d.py.
"""

import os
import streamlit as st

from flower_core import make_flower, floral_formula, traits_text, WHORL_ORDER, WHORL_LABEL
from flower3d import build_flower
from ovary_section import cross_section, PLACENTATION_CHOICES
from glossary import GLOSSARY, CATEGORIES
from special_cases import SPECIALS, draw_special, WHY_BRUSH
from fruits import FRUITS, draw_fruit, draw_overview, OVERVIEW_TEXT

st.set_page_config(page_title="Flower Dissection", page_icon="🌸", layout="wide")

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
def new_flower():
    st.session_state.flower = make_flower()
    st.session_state.flower_id = st.session_state.get("flower_id", 0) + 1
    st.session_state.removed = set()
    st.session_state.feedback = ""
    st.session_state.feedback_kind = ""

def init():
    if "flower" not in st.session_state:
        st.session_state.score = 0
        st.session_state.scored = set()      # (flower_id, mode) already scored
        st.session_state.mode = "Peel and name"
        new_flower()

init()

MODES = ["Peel and name", "Label the parts", "Count and describe",
         "Inside the ovary", "Special cases", "Fruits", "Glossary"]

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    "<h2 style='margin-bottom:0'>🌸 Flower Dissection</h2>"
    "<p style='color:#5c6f66;margin-top:2px'>A generic flower, freshly grown and "
    "randomised each round. Pull it apart, label it, or describe it.</p>",
    unsafe_allow_html=True,
)

top = st.columns([3.4, 0.4, 1.3, 1.1])
with top[0]:
    mode = st.radio("Mode", MODES, horizontal=True,
                    index=MODES.index(st.session_state.mode), label_visibility="collapsed")
    st.session_state.mode = mode
with top[2]:
    if st.button("🌱 New flower", use_container_width=True):
        new_flower()
        st.rerun()
with top[3]:
    st.metric("Score", st.session_state.score)

f = st.session_state.flower
mode = st.session_state.mode

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def award(points, key):
    """Add points once per (flower, mode) key."""
    tag = (st.session_state.flower_id, key)
    if tag not in st.session_state.scored:
        st.session_state.scored.add(tag)
        st.session_state.score += points

def show_formula():
    st.markdown(
        f"<div style='background:#22463d;color:#eaf6ea;border-radius:10px;"
        f"padding:12px 16px;font-size:20px;font-family:Cambria,Georgia,serif'>"
        f"<span style='font-size:11px;color:#cfe0c8;letter-spacing:.5px'>FLORAL FORMULA</span><br>"
        f"{floral_formula(f)}</div>",
        unsafe_allow_html=True,
    )
    st.caption(traits_text(f))

# ----------------------------------------------------------------------
# Layout: flower on the left, interaction on the right
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Special cases is a full-width tab, handled before the game layout
# ----------------------------------------------------------------------
if mode == "Special cases":
    st.markdown("### Special cases")
    st.write("Some Australian flowers break the generic-flower rules. Pick one, see "
             "what is special, then take the short quiz.")
    names = [s["name"] for s in SPECIALS]
    choice = st.selectbox("Choose a special case", names, key="special_choice")
    entry = next(s for s in SPECIALS if s["name"] == choice)
    scl, scr = st.columns([1.1, 1])
    with scl:
        st.pyplot(draw_special(entry["key"]), clear_figure=True)
    with scr:
        title = f"*{entry['name']}*" if entry["italic"] else entry["name"]
        st.markdown(f"**{title}**  \n{entry['family']}")
        st.write(entry["special"])
        st.caption(f"[Read more on Wikipedia]({entry['wiki']})")
        with st.form(f"scform_{entry['key']}"):
            picks = []
            for i, qq in enumerate(entry["quiz"]):
                picks.append(st.radio(qq["q"], ["(choose)"] + qq["options"], index=0,
                                      key=f"scq_{entry['key']}_{i}"))
            submitted = st.form_submit_button("Check answers", use_container_width=True)
        if submitted:
            correct = 0
            for qq, p in zip(entry["quiz"], picks):
                ok = p == qq["answer"]
                correct += ok
                st.markdown(f"{'✅' if ok else '❌'} {qq['q']} — "
                            f"{'correct' if ok else 'answer is ' + qq['answer']}")
            done = st.session_state.setdefault("special_done", set())
            if entry["key"] not in done:
                done.add(entry["key"])
                st.session_state.score += correct
            (st.success if correct == len(entry["quiz"]) else st.info)(
                f"{correct} of {len(entry['quiz'])} correct.")
    st.divider()
    with st.expander("Why is the showy part so often the stamens?"):
        st.markdown(WHY_BRUSH)
    st.stop()

# ----------------------------------------------------------------------
# Fruits is a full-width tab, handled before the game layout
# ----------------------------------------------------------------------
if mode == "Fruits":
    st.markdown("### Fruit types")
    st.write("After a flower is pollinated it can ripen into a fruit. See how the "
             "parts map over, then step through the different fruit types.")
    with st.expander("How flower parts become fruit parts", expanded=True):
        oc1, oc2 = st.columns([1.25, 1])
        with oc1:
            st.pyplot(draw_overview(), clear_figure=True)
        with oc2:
            st.markdown(OVERVIEW_TEXT)
            _gif = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "flower_to_fruit.gif")
            if os.path.exists(_gif):
                st.image(_gif, caption="The ovary ripening into the fruit", width=340)
    names = [fr["name"] for fr in FRUITS]
    choice = st.selectbox("Choose a fruit type", names, key="fruit_choice")
    entry = next(fr for fr in FRUITS if fr["name"] == choice)
    fcl, fcr = st.columns([1.1, 1])
    with fcl:
        st.pyplot(draw_fruit(entry["key"]), clear_figure=True)
    with fcr:
        st.markdown(f"**{entry['name']}**  \n{entry['group']}")
        st.write(entry["text"])
        st.caption(f"[Read more on Wikipedia]({entry['wiki']})")
        with st.form(f"frform_{entry['key']}"):
            picks = []
            for i, qq in enumerate(entry["quiz"]):
                picks.append(st.radio(qq["q"], ["(choose)"] + qq["options"], index=0,
                                      key=f"frq_{entry['key']}_{i}"))
            submitted = st.form_submit_button("Check answers", use_container_width=True)
        if submitted:
            correct = 0
            for qq, p in zip(entry["quiz"], picks):
                ok = p == qq["answer"]
                correct += ok
                st.markdown(f"{'✅' if ok else '❌'} {qq['q']} — "
                            f"{'correct' if ok else 'answer is ' + qq['answer']}")
            done = st.session_state.setdefault("fruit_done", set())
            if entry["key"] not in done:
                done.add(entry["key"])
                st.session_state.score += correct
            (st.success if correct == len(entry["quiz"]) else st.info)(
                f"{correct} of {len(entry['quiz'])} correct.")
    st.stop()

# ----------------------------------------------------------------------
# Glossary is a full-width reference tab, handled before the game layout
# ----------------------------------------------------------------------
if mode == "Glossary":
    st.markdown("### Glossary of flower parts")
    st.write("Each term has a diagram from this tool and a link to its Wikipedia "
             "article.")
    q = st.text_input("Search", "", placeholder="Type a term, for example stigma").strip().lower()
    IMGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glossary_images")
    shown = [g for g in GLOSSARY
             if not q or q in g["term"].lower() or q in g["definition"].lower()]
    if not shown:
        st.info("No terms match that search.")
    for cat in CATEGORIES:
        items = [g for g in shown if g["cat"] == cat]
        if not items:
            continue
        st.markdown(f"#### {cat}")
        for g in items:
            c1, c2 = st.columns([1, 1.7])
            with c1:
                img = os.path.join(IMGDIR, g["image"])
                if os.path.exists(img):
                    st.image(img, width=300)
            with c2:
                st.markdown(f"**{g['term']}**")
                st.write(g["definition"])
                st.caption(f"Diagram from this tool · [read more on Wikipedia]({g['wiki']})")
            st.divider()
    st.stop()

left, right = st.columns([1.15, 1])

# --- decide what to draw for the current mode ---
removed = st.session_state.removed
if mode == "Inside the ovary":
    ofig, ohot, oans, oexplain, onames = cross_section(f)
    with left:
        st.pyplot(ofig, clear_figure=True)
        st.caption("Transverse section — a cut straight across the ovary.")
else:
    if mode == "Peel and name":
        target = next((w for w in WHORL_ORDER if w not in removed), None)
        fig, hotspots = build_flower(f, removed=removed, highlight=target)
    elif mode == "Label the parts":
        fig, hotspots = build_flower(f, show_numbers=True)
    else:
        fig, hotspots = build_flower(f)
    with left:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                        key=f"flower3d_{st.session_state.flower_id}")
        st.caption("Drag to rotate · scroll to zoom · double-click to reset the view")

# ----------------------------------------------------------------------
# Mode: PEEL AND NAME
# ----------------------------------------------------------------------
with right:
    if mode == "Peel and name":
        st.subheader("Peel and name")
        done = len([w for w in WHORL_ORDER if w in removed])
        st.progress(done / 4, text=f"{done} / 4 whorls removed")
        if target is None:
            st.success("Every whorl removed. This flower is fully dissected.")
            show_formula()
        else:
            st.write("Work from the outside in. The vivid whorl is the outermost one "
                     "still attached. Name it and it peels away.")
            cols = st.columns(2)
            for i, w in enumerate(WHORL_ORDER):
                with cols[i % 2]:
                    if st.button(WHORL_LABEL[w], key=f"peel_{w}", use_container_width=True):
                        if w == target:
                            st.session_state.removed = removed | {w}
                            award(1, f"peel_{w}")
                            st.session_state.feedback = f"Correct. That is the {WHORL_LABEL[w].lower()}."
                            st.session_state.feedback_kind = "good"
                        else:
                            st.session_state.feedback = ("Not that one. The outermost attached "
                                                         "whorl is the vivid one.")
                            st.session_state.feedback_kind = "bad"
                        st.rerun()
        if st.session_state.feedback:
            (st.success if st.session_state.feedback_kind == "good" else st.error)(
                st.session_state.feedback)

    # ------------------------------------------------------------------
    # Mode: LABEL THE PARTS
    # ------------------------------------------------------------------
    elif mode == "Label the parts":
        st.subheader("Label the parts")
        st.write("Match each numbered marker on the flower to the name of that part.")
        names = [h["name"] for h in hotspots]
        options = ["—"] + names
        with st.form("label_form"):
            picks = {}
            for h in hotspots:
                picks[h["num"]] = st.selectbox(
                    f"Part {h['num']}", options, key=f"lab_{h['num']}")
            submitted = st.form_submit_button("Check answers", use_container_width=True)
        if submitted:
            correct = 0
            lines = []
            for h in hotspots:
                ok = picks[h["num"]] == h["name"]
                correct += ok
                lines.append(f"{'✅' if ok else '❌'} **{h['num']}** — "
                             f"{'correct' if ok else 'that is the ' + h['name'].lower()}")
            award(correct, "label")
            st.markdown("\n\n".join(lines))
            (st.success if correct == len(hotspots) else st.info)(
                f"{correct} of {len(hotspots)} parts named correctly.")
            show_formula()

    # ------------------------------------------------------------------
    # Mode: COUNT AND DESCRIBE
    # ------------------------------------------------------------------
    elif mode == "Count and describe":
        st.subheader("Count and describe")
        st.write("Study the whole flower, then answer each question and check.")
        with st.form("count_form"):
            c1, c2 = st.columns(2)
            with c1:
                a_sep = st.number_input("How many sepals?", 1, 12, 1)
                a_sta = st.number_input("How many stamens?", 1, 12, 1)
                a_sym = st.selectbox("Floral symmetry?",
                                     ["—", "Actinomorphic (radial)", "Zygomorphic (bilateral)"])
            with c2:
                a_pet = st.number_input("How many petals?", 1, 12, 1)
                a_car = st.number_input("How many carpels?", 1, 12, 1)
                a_fus = st.selectbox("Are the petals fused?",
                                     ["—", "Free (separate)", "Fused (sympetalous)"])
            submitted = st.form_submit_button("Check answers", use_container_width=True)
        if submitted:
            sym_val = {"Actinomorphic (radial)": "radial",
                       "Zygomorphic (bilateral)": "bilateral"}.get(a_sym)
            fus_val = {"Free (separate)": "free",
                       "Fused (sympetalous)": "fused"}.get(a_fus)
            checks = [
                ("Sepals", a_sep == f["sepals"], f["sepals"]),
                ("Petals", a_pet == f["petals"], f["petals"]),
                ("Stamens", a_sta == f["stamens"], f["stamens"]),
                ("Carpels", a_car == f["carpels"], f["carpels"]),
                ("Symmetry", sym_val == f["symmetry"], f["symmetry"]),
                ("Petal fusion", fus_val == f["petal_fusion"], f["petal_fusion"]),
            ]
            correct = sum(1 for _, ok, _ in checks)
            award(correct, "count")
            for label, ok, ans in checks:
                st.markdown(f"{'✅' if ok else '❌'} **{label}** — "
                            f"{'correct' if ok else f'answer is {ans}'}")
            (st.success if correct == 6 else st.info)(f"{correct} of 6 correct.")
            show_formula()

    # ------------------------------------------------------------------
    # Mode: INSIDE THE OVARY
    # ------------------------------------------------------------------
    elif mode == "Inside the ovary":
        st.subheader("Inside the ovary")
        st.write("This is a cut straight across the ovary. Match each numbered part, "
                 "then say how many locules there are and which type of placentation.")
        options = ["—"] + onames
        with st.form("ovary_form"):
            picks = {}
            for h in ohot:
                picks[h["num"]] = st.selectbox(f"Part {h['num']}", options,
                                               key=f"ov_{h['num']}")
            st.markdown("**Then describe the ovary**")
            oc1, oc2 = st.columns(2)
            with oc1:
                a_loc = st.number_input("How many locules?", 1, 12, 1)
            with oc2:
                a_plac = st.selectbox("Placentation?", ["—"] + PLACENTATION_CHOICES)
            submitted = st.form_submit_button("Check answers", use_container_width=True)
        if submitted:
            correct = 0
            lines = []
            for h in ohot:
                ok = picks[h["num"]] == h["name"]
                correct += ok
                lines.append(f"{'✅' if ok else '❌'} **{h['num']}** — "
                             f"{'correct' if ok else 'that is the ' + h['name'].lower()}")
            loc_ok = a_loc == oans["locules"]
            plac_ok = a_plac == oans["placentation"]
            correct += loc_ok + plac_ok
            total = len(ohot) + 2
            award(correct, "ovary")
            st.markdown("\n\n".join(lines))
            st.markdown(f"{'✅' if loc_ok else '❌'} **Locules** — "
                        f"{'correct' if loc_ok else 'answer is ' + str(oans['locules'])}")
            st.markdown(f"{'✅' if plac_ok else '❌'} **Placentation** — "
                        f"{'correct' if plac_ok else 'answer is ' + oans['placentation']}")
            (st.success if correct == total else st.info)(f"{correct} of {total} correct.")
            st.info(oexplain)

    with st.expander("Reveal the floral formula"):
        show_formula()

st.caption("Generic teaching flower. Structures are illustrative, not to scale. Built for BIO262.")
