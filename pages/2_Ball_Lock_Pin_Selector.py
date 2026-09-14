"""Interactive sizing and checking page for a ball-lock quick-release pin."""

import math

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from mechanics.ball_lock import (
    analyze_pin,
    required_diameter_for_bearing,
    required_diameter_for_shear,
    select_standard_diameter,
    solve_shear_relationship,
)
from mechanics.plots import ball_lock_figure
from mechanics.units import IN_TO_MM
from ui import default, hero, number, setup_page, status_box, unit_selector


setup_page("Ball-Lock Pin Selector", "📌")
units = unit_selector("ball_units")
unit_key = "si" if units.is_si else "us"
hero(
    "Ball-Lock Pin Selector",
    "Size the pin body for transverse loading, fit the grip to the joint stack, and verify axial retention from catalog data.",
)

st.markdown(
    '<div class="callout"><strong>Three separate decisions:</strong> diameter carries transverse load; '
    'grip length spans the assembled stack; manufacturer-rated ball retention resists axial pull-out. '
    'Passing one check does not guarantee the others.</div>',
    unsafe_allow_html=True,
)

motion_tab, size_tab, check_tab, solve_tab = st.tabs(
    ["Operation explorer", "Size a new pin", "Check an existing pin", "Solve shear relationship"]
)


def joint_inputs(prefix: str):
    shear_planes = st.radio(
        "Joint arrangement",
        [2, 1],
        format_func=lambda value: "Double shear (clevis)" if value == 2 else "Single shear",
        horizontal=True,
        key=f"{prefix}_planes_{unit_key}",
    )
    cols = st.columns(3)
    with cols[0]:
        center_t = number(
            f"Center-member thickness ({units.length})",
            default(units, 8.0, 0.31),
            key=f"{prefix}_center_t_{unit_key}",
            minimum=0.001,
            step=default(units, 0.5, 0.01),
        )
    with cols[1]:
        outer_t = number(
            f"Each outer-lug thickness ({units.length})",
            default(units, 6.0, 0.24),
            key=f"{prefix}_outer_t_{unit_key}",
            minimum=0.001,
            step=default(units, 0.5, 0.01),
            help_text="Used directly for a double-shear clevis. For single shear, the center-member thickness controls the simplified bearing check.",
        )
    with cols[2]:
        bearing_allow = number(
            f"Member bearing limit before FOS ({units.stress})",
            default(units, 200.0, 29.0),
            key=f"{prefix}_bearing_{unit_key}",
            minimum=0.001,
            step=default(units, 10.0, 1.0),
        )
    return shear_planes, center_t, outer_t, bearing_allow


def grip_inputs(prefix: str, center_t: float, outer_t: float, shear_planes: int):
    nominal_stack = center_t + (2.0 * outer_t if shear_planes == 2 else outer_t)
    c1, c2 = st.columns(2)
    with c1:
        stack = number(
            f"Measured assembled stack ({units.length})",
            nominal_stack,
            key=f"{prefix}_stack_{unit_key}",
            minimum=0.001,
            step=default(units, 0.5, 0.01),
            help_text="Use the actual distance the pin must span, including washers or spacers.",
        )
    with c2:
        clearance = number(
            f"Added grip allowance ({units.length})",
            default(units, 0.5, 0.02),
            key=f"{prefix}_clearance_{unit_key}",
            minimum=0.0,
            step=default(units, 0.1, 0.005),
        )
    return stack, clearance


def axial_rating_inputs(prefix: str):
    use_rating = st.checkbox(
        "I have axial pull-out data for the exact candidate pin",
        key=f"{prefix}_use_rating_{unit_key}",
    )
    if not use_rating:
        return None, True
    c1, c2 = st.columns(2)
    with c1:
        rating = number(
            f"Catalog axial pull-out rating ({units.force})",
            default(units, 2000.0, 450.0),
            key=f"{prefix}_rating_{unit_key}",
            minimum=0.001,
            step=default(units, 100.0, 25.0),
        )
    with c2:
        rating_kind = st.selectbox(
            "How is that rating defined?",
            ["Allowable / already includes safety factor", "Failure or ultimate rating"],
            key=f"{prefix}_rating_kind_{unit_key}",
        )
    return rating, rating_kind.startswith("Allowable")


with motion_tab:
    controls, visual = st.columns([0.75, 1.65], gap="large")
    with controls:
        insertion = st.slider(
            "Insertion through joint",
            0.0,
            1.0,
            1.0,
            0.05,
            key=f"ball_insertion_{unit_key}",
        )
        pressed = st.toggle("Release button pressed", value=False, key=f"ball_pressed_{unit_key}")
        if pressed:
            st.info("The internal plunger permits the balls to retract so the pin can move through the holes.")
        else:
            st.success("The spring returns the plunger and forces the balls outward to obstruct withdrawal.")
    with visual:
        fig = ball_lock_figure(pressed, insertion)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.caption("Use both controls to model insertion, locking, and release.")

with size_tab:
    st.write("Enter the design loads and joint details. The suggested body diameter is the larger value required by uniform pin shear or simplified plate bearing.")
    a, b, c = st.columns(3)
    with a:
        transverse_load = number(f"Design transverse load ({units.force})", default(units, 1500.0, 340.0), key=f"size_ft_{unit_key}", minimum=0.001, step=default(units, 100.0, 25.0))
    with b:
        axial_load = number(f"Design axial pull-out load ({units.force})", default(units, 300.0, 70.0), key=f"size_fa_{unit_key}", minimum=0.0, step=default(units, 50.0, 10.0))
    with c:
        fos = number("Design factor of safety", 2.0, key=f"size_fos_{unit_key}", minimum=1.0, step=0.1)
    pin_yield = number(f"Pin-body yield strength ({units.stress})", default(units, 600.0, 87.0), key=f"size_sy_{unit_key}", minimum=0.001, step=default(units, 10.0, 1.0))
    shear_planes, center_t, outer_t, bearing_allow = joint_inputs("size")
    stack, clearance = grip_inputs("size", center_t, outer_t, shear_planes)
    rating, rating_is_allowable = axial_rating_inputs("size")

    try:
        shear_d_si = required_diameter_for_shear(
            units.force_to_si(transverse_load),
            units.stress_to_si(pin_yield),
            fos,
            shear_planes,
        )
        bearing_d_si = required_diameter_for_bearing(
            units.force_to_si(transverse_load),
            units.length_to_si(center_t),
            units.length_to_si(outer_t),
            units.stress_to_si(bearing_allow),
            fos,
            shear_planes,
        )
        required_si = max(shear_d_si, bearing_d_si)
        if units.is_si:
            standard_options = [5, 6, 8, 10, 12, 16, 20, 25, 30]
            selected_si = select_standard_diameter(required_si, standard_options)
            selected_display = selected_si
        else:
            standard_in = [3/16, 1/4, 5/16, 3/8, 7/16, 1/2, 9/16, 5/8, 3/4, 7/8, 1.0, 1.25]
            selected_si = select_standard_diameter(required_si, [value * IN_TO_MM for value in standard_in])
            selected_display = None if selected_si is None else units.length_from_si(selected_si)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Diameter from shear", f"{units.length_from_si(shear_d_si):.3f} {units.length}")
        m2.metric("Diameter from bearing", f"{units.length_from_si(bearing_d_si):.3f} {units.length}")
        m3.metric("Required minimum diameter", f"{units.length_from_si(required_si):.3f} {units.length}")
        m4.metric("Suggested standard diameter", "Above list" if selected_si is None else f"{selected_display:g} {units.length}")
        st.metric("Required minimum grip length", f"{stack + clearance:.3f} {units.length}")
        st.caption("The standard-size list is only a rounding aid; confirm available diameter, grip increments, tolerance, material, and ratings in the selected manufacturer’s catalog.")

        if rating is None:
            st.warning("Axial pull-out is not yet verified. Add an exact manufacturer rating above before selecting the pin.")
        else:
            allowable = rating if rating_is_allowable else rating / fos
            margin = math.inf if axial_load == 0 else allowable / axial_load
            status_box(
                margin >= 1.0,
                f"Axial catalog check passes with margin {margin:.2f}.",
                f"Axial catalog check fails; margin is {margin:.2f}.",
            )
    except ValueError as exc:
        st.error(str(exc))

with check_tab:
    st.write("Check a known pin against transverse shear, member bearing, grip length, and—when supplied—manufacturer-rated axial retention.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        diameter = number(f"Candidate pin diameter ({units.length})", default(units, 8.0, 0.3125), key=f"check_d_{unit_key}", minimum=0.001, step=default(units, 0.5, 0.0625))
    with c2:
        transverse = number(f"Applied transverse load ({units.force})", default(units, 1500.0, 340.0), key=f"check_ft_{unit_key}", minimum=0.0, step=default(units, 100.0, 25.0))
    with c3:
        axial = number(f"Applied axial load ({units.force})", default(units, 300.0, 70.0), key=f"check_fa_{unit_key}", minimum=0.0, step=default(units, 50.0, 10.0))
    with c4:
        check_fos = number("Design factor of safety", 2.0, key=f"check_fos_{unit_key}", minimum=1.0, step=0.1)
    check_sy = number(f"Pin-body yield strength ({units.stress})", default(units, 600.0, 87.0), key=f"check_sy_{unit_key}", minimum=0.001, step=default(units, 10.0, 1.0))
    check_planes, check_center, check_outer, check_bearing = joint_inputs("check")
    check_stack, check_clearance = grip_inputs("check", check_center, check_outer, check_planes)
    candidate_grip = number(f"Candidate nominal grip length ({units.length})", default(units, 21.0, 0.85), key=f"check_grip_{unit_key}", minimum=0.001, step=default(units, 0.5, 0.01))
    check_rating, check_rating_is_allowable = axial_rating_inputs("check")

    try:
        result = analyze_pin(
            diameter_mm=units.length_to_si(diameter),
            transverse_load_n=units.force_to_si(transverse),
            axial_load_n=units.force_to_si(axial),
            pin_yield_mpa=units.stress_to_si(check_sy),
            center_thickness_mm=units.length_to_si(check_center),
            outer_thickness_mm=units.length_to_si(check_outer),
            total_stack_mm=units.length_to_si(check_stack),
            grip_clearance_mm=units.length_to_si(check_clearance),
            bearing_allowable_mpa=units.stress_to_si(check_bearing),
            factor_of_safety=check_fos,
            shear_planes=check_planes,
            axial_rating_n=None if check_rating is None else units.force_to_si(check_rating),
            axial_rating_is_allowable=check_rating_is_allowable,
        )
        r1, r2, r3 = st.columns(3)
        r1.metric("Transverse capacity", f"{units.force_from_si(result.transverse_capacity_n):,.1f} {units.force}")
        r2.metric("Transverse margin", "∞" if math.isinf(result.transverse_margin) else f"{result.transverse_margin:.2f}")
        r3.metric("Governing transverse check", result.governing_mode)
        status_box(result.transverse_margin >= 1.0, "Transverse screening checks pass.", "At least one transverse screening check fails.")

        required_grip = units.length_from_si(result.required_grip_mm)
        status_box(
            candidate_grip >= required_grip,
            f"Grip check passes: {candidate_grip:.3f} {units.length} ≥ {required_grip:.3f} {units.length} required.",
            f"Grip check fails: {candidate_grip:.3f} {units.length} < {required_grip:.3f} {units.length} required.",
        )

        if result.axial_margin is None:
            st.warning("Axial retention remains unverified because no exact catalog pull-out rating was supplied.")
        else:
            status_box(
                result.axial_margin >= 1.0,
                f"Axial catalog check passes with margin {result.axial_margin:.2f}.",
                f"Axial catalog check fails; margin is {result.axial_margin:.2f}.",
            )

        stress_rows = pd.DataFrame(
            {
                "Screen": ["Pin shear", "Center-member bearing", "Outer-lug bearing"],
                f"Calculated stress ({units.stress})": [
                    units.stress_from_si(result.pin_shear_stress_mpa),
                    units.stress_from_si(result.center_bearing_stress_mpa),
                    units.stress_from_si(result.outer_bearing_stress_mpa),
                ],
            }
        ).round(3)
        st.dataframe(stress_rows, use_container_width=True, hide_index=True)
    except ValueError as exc:
        st.error(str(exc))

with solve_tab:
    st.write("Solve the static uniform-shear relationship for one selected quantity. Plate bearing and axial pull-out are separate checks.")
    unknown = st.selectbox(
        "Quantity to calculate",
        ["Pin diameter", "Maximum transverse load", "Actual factor of safety"],
        key=f"ball_solve_unknown_{unit_key}",
    )
    cols = st.columns(4)
    diameter_s = load_s = fos_s = None
    with cols[0]:
        sy_s = number(f"Pin yield strength ({units.stress})", default(units, 600.0, 87.0), key=f"solve_ball_sy_{unknown}_{unit_key}", minimum=0.001, step=default(units, 10.0, 1.0))
    with cols[1]:
        planes_s = st.radio("Shear planes", [1, 2], horizontal=True, index=1, key=f"solve_ball_planes_{unknown}_{unit_key}")
    if unknown != "Pin diameter":
        with cols[2]:
            diameter_s = number(f"Pin diameter ({units.length})", default(units, 8.0, 0.3125), key=f"solve_ball_d_{unknown}_{unit_key}", minimum=0.001, step=default(units, 0.5, 0.0625))
    if unknown != "Maximum transverse load":
        target_col = cols[3] if unknown != "Pin diameter" else cols[2]
        with target_col:
            load_s = number(f"Transverse load ({units.force})", default(units, 1500.0, 340.0), key=f"solve_ball_f_{unknown}_{unit_key}", minimum=0.001, step=default(units, 100.0, 25.0))
    if unknown != "Actual factor of safety":
        target_col = cols[3]
        with target_col:
            fos_s = number("Factor of safety", 2.0, key=f"solve_ball_fos_{unknown}_{unit_key}", minimum=1.0, step=0.1)
    try:
        solved = solve_shear_relationship(
            unknown,
            diameter_mm=None if diameter_s is None else units.length_to_si(diameter_s),
            transverse_load_n=None if load_s is None else units.force_to_si(load_s),
            pin_yield_mpa=units.stress_to_si(sy_s),
            factor_of_safety=fos_s,
            shear_planes=planes_s,
        )
        if unknown == "Pin diameter":
            st.metric("Required pin diameter", f"{units.length_from_si(solved):.3f} {units.length}")
        elif unknown == "Maximum transverse load":
            st.metric("Maximum screened transverse load", f"{units.force_from_si(solved):,.1f} {units.force}")
        else:
            st.metric("Actual shear factor of safety", f"{solved:.2f}")
    except (TypeError, ValueError) as exc:
        st.error(str(exc))

with st.expander("What the calculator assumes"):
    st.markdown(
        """
The transverse model assumes static loading, an aligned joint, uniform pin
shear, and projected-area bearing. Pin shear yielding is estimated with
τy = Sy/√3. It does not check pin bending, hole tear-out, net-section rupture,
fatigue, shock, corrosion, tolerance, wear, or joint separation.

The retaining balls are a release feature, not a universal axial-capacity
formula. Axial strength depends on the complete manufactured assembly and the
receiving-hole geometry. For that reason, the app only accepts an axial rating
from the exact manufacturer's data rather than inventing one from ball size.
"""
    )

with st.expander("Sources and verification trail"):
    st.markdown(
        """
- Carr Lane Manufacturing, [“Ball Lock Pins—How They Work”](https://www.carrlane.com/engineering-resources/technical-information/ball-lock-pins-engineering-application/how-ball-lock-pins-work) and [“Ball Lock Pin Technical Information”](https://www.carrlane.com/engineering-resources/technical-information/manual-workholding/ball-lock-pin-technical-information) (operation, grip definition, and catalog strength data).
- [Budynas, R. G. and Nisbett, J. K., *Shigley’s Mechanical Engineering Design*, McGraw Hill](https://www.mheducation.com/highered/product/shigleys-mechanical-engineering-design-nisbett) (pin shear, bearing stress, and safety-factor checks).

Always use the selected manufacturer’s dimensional table and ratings for the exact part number. Catalog conventions may already include a safety factor; the rating-definition control prevents the app from applying it twice.
"""
    )
