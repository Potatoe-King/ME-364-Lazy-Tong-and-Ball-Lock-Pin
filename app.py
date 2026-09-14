"""Landing page for the ME 36400 mechanism design tools."""

import streamlit as st

from ui import hero, setup_page


setup_page("ME 36400 Mechanism Design Tools", "🧰")
hero(
    "Mechanism Design Tools",
    "Explore, size, and check a lazy-tong linkage or ball-detent quick-release pin.",
)

st.markdown(
    """
These tools turn the two mechanisms into design decisions. Use the pages in the
sidebar to move between an ideal geometry model, inverse sizing, and preliminary
strength checks. Every result states the assumptions behind it so the output can
be verified rather than accepted blindly.
"""
)

left, right = st.columns(2, gap="large")
with left:
    st.subheader("Lazy-tong linkage")
    st.markdown(
        """
- Animate extension and retraction.
- Solve for length, link size, angle, or stage count.
- Search for geometries that fit a retracted and extended envelope.
- Estimate axial capacity from link yielding, buckling, pin shear, and bearing.
"""
    )
    st.page_link("pages/1_Lazy_Tong_Designer.py", label="Open Lazy-Tong Designer", icon="↗️")

with right:
    st.subheader("Ball-lock pin")
    st.markdown(
        """
- Animate insertion and button release.
- Size the pin for transverse shear and plate bearing.
- Select a minimum grip length from the joint stack.
- Check an existing pin and audit axial retention against catalog data.
"""
    )
    st.page_link("pages/2_Ball_Lock_Pin_Selector.py", label="Open Ball-Lock Pin Selector", icon="↗️")

st.markdown(
    """
<div class="callout warning-callout">
<strong>Scope:</strong> This is a preliminary educational design aid. It does not
replace a manufacturer rating, detailed joint analysis, finite-element analysis,
prototype testing, or review by a qualified engineer. Do not use it for
life-safety hardware.
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("Model boundaries"):
    st.markdown(
        """
**Lazy tong:** rigid links, ideal revolute joints, symmetric in-plane motion, and
centered axial loading. The capacity model omits eccentricity, joint clearance,
pin bending, tear-out, fatigue, out-of-plane buckling, and horizontal tip-load
bending.

**Ball-lock pin:** static transverse load, uniform shear, simple projected-area
bearing, and an aligned joint. Axial retention is not predicted from ball
geometry; it must be checked using the exact manufacturer's rating for the chosen
pin, grip, material, and receiving-hole geometry.
"""
    )

st.caption("ME 36400 educational package • SI and US customary inputs supported")

