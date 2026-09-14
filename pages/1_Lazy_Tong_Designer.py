"""Interactive lazy-tong geometry, synthesis, and preliminary strength page."""

import math

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from mechanics.lazy_tong import (
    geometry,
    preliminary_capacity,
    solve_configuration,
    synthesize_envelope,
)
from mechanics.plots import lazy_tong_figure
from ui import default, hero, number, setup_page, status_box, unit_selector


setup_page("Lazy-Tong Designer", "📐")
units = unit_selector("lazy_units")
unit_key = "si" if units.is_si else "us"
hero(
    "Lazy-Tong Designer",
    "Move from a desired package and reach to stage geometry, then screen the linkage for axial capacity.",
)

st.markdown(
    '<div class="callout"><strong>Ideal geometry:</strong> each stage has axial projection '
    '<em>L cos θ</em> and pivot-to-pivot height <em>L sin θ</em>. The model uses full '
    'pivot-to-pivot link length <em>L</em>.</div>',
    unsafe_allow_html=True,
)

motion_tab, solve_tab, envelope_tab, capacity_tab = st.tabs(
    ["Motion explorer", "Solve one unknown", "Fit an envelope", "Capacity screen"]
)

with motion_tab:
    input_col, visual_col = st.columns([0.82, 1.6], gap="large")
    with input_col:
        stages = st.slider("Complete stages", 1, 12, 5, key=f"motion_n_{unit_key}")
        link_length = number(
            f"Link length, L ({units.length})",
            default(units, 250.0, 10.0),
            key=f"motion_L_{unit_key}",
            minimum=0.01,
            step=default(units, 5.0, 0.1),
        )
        angle = st.slider(
            "Link angle, θ (degrees)",
            5.0,
            80.0,
            35.0,
            1.0,
            key=f"motion_theta_{unit_key}",
        )
        result = geometry(stages, units.length_to_si(link_length), angle)
        x = units.length_from_si(result.axial_length_mm)
        y = units.length_from_si(result.transverse_height_mm)
        m1, m2 = st.columns(2)
        m1.metric("Axial length", f"{x:,.2f} {units.length}")
        m2.metric("Stage height", f"{y:,.2f} {units.length}")
        st.caption("Stage height is between corresponding upper and lower pivots, not the outside package size.")
    with visual_col:
        fig = lazy_tong_figure(stages, angle)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.caption("Move the angle slider to animate extension and retraction.")

with solve_tab:
    st.write("Choose one unknown. The app solves the ideal relationship x = nL cos(θ).")
    unknown = st.selectbox(
        "Quantity to calculate",
        ["Stage count", "Link length", "Link angle", "Axial length"],
        key=f"lazy_unknown_{unit_key}",
    )
    c1, c2, c3 = st.columns(3)
    x_input = n_input = l_input = theta_input = None
    fields = [name for name in ["Axial length", "Stage count", "Link length", "Link angle"] if name != unknown]
    containers = [c1, c2, c3]
    for name, container in zip(fields, containers):
        with container:
            if name == "Axial length":
                x_input = number(
                    f"Known axial length ({units.length})",
                    default(units, 900.0, 36.0),
                    key=f"solve_x_{unknown}_{unit_key}",
                    minimum=0.01,
                    step=default(units, 10.0, 0.25),
                )
            elif name == "Stage count":
                n_input = st.number_input(
                    "Known complete stages", 1, 50, 5, 1, key=f"solve_n_{unknown}_{unit_key}"
                )
            elif name == "Link length":
                l_input = number(
                    f"Known link length ({units.length})",
                    default(units, 250.0, 10.0),
                    key=f"solve_L_{unknown}_{unit_key}",
                    minimum=0.01,
                    step=default(units, 5.0, 0.1),
                )
            else:
                theta_input = number(
                    "Known link angle (degrees)",
                    35.0,
                    key=f"solve_theta_{unknown}_{unit_key}",
                    minimum=0.1,
                    step=1.0,
                )
    try:
        solved = solve_configuration(
            unknown,
            axial_length_mm=None if x_input is None else units.length_to_si(x_input),
            stages=n_input,
            link_length_mm=None if l_input is None else units.length_to_si(l_input),
            angle_deg=theta_input,
        )
        if unknown == "Stage count":
            st.metric("Minimum whole stages", f"{int(solved['stages'])}")
            st.caption(
                f"Continuous result: {solved['stage_count_continuous']:.2f}; achieved axial length after rounding: "
                f"{units.length_from_si(solved['achieved_length_mm']):.2f} {units.length}."
            )
        elif unknown == "Link length":
            st.metric("Required link length", f"{units.length_from_si(solved['link_length_mm']):.2f} {units.length}")
        elif unknown == "Link angle":
            st.metric("Required link angle", f"{solved['angle_deg']:.2f}°")
        else:
            st.metric("Axial length", f"{units.length_from_si(solved['axial_length_mm']):.2f} {units.length}")
    except (TypeError, ValueError) as exc:
        st.error(str(exc))

with envelope_tab:
    st.write(
        "Enter an exact retracted pivot envelope and a target extended length. The search returns every integer stage count that reaches the target without going below the selected minimum angle."
    )
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        x_retracted = number(
            f"Retracted axial length ({units.length})",
            default(units, 450.0, 18.0),
            key=f"env_xr_{unit_key}",
            minimum=0.01,
            step=default(units, 10.0, 0.25),
        )
    with e2:
        x_extended = number(
            f"Desired extended length ({units.length})",
            default(units, 1000.0, 40.0),
            key=f"env_xe_{unit_key}",
            minimum=0.01,
            step=default(units, 10.0, 0.25),
        )
    with e3:
        y_retracted = number(
            f"Retracted pivot height ({units.length})",
            default(units, 220.0, 8.5),
            key=f"env_yr_{unit_key}",
            minimum=0.01,
            step=default(units, 5.0, 0.1),
        )
    with e4:
        minimum_angle = number(
            "Minimum operating angle (degrees)",
            10.0,
            key=f"env_min_angle_{unit_key}",
            minimum=0.1,
            step=1.0,
            help_text="Avoids a nearly flat geometry, where small motions and imperfections become especially influential.",
        )
    r1, r2 = st.columns(2)
    with r1:
        minimum_stages = st.number_input("Minimum stages", 1, 30, 2, 1, key=f"env_nmin_{unit_key}")
    with r2:
        maximum_stages = st.number_input("Maximum stages", 1, 50, 12, 1, key=f"env_nmax_{unit_key}")

    try:
        candidates = synthesize_envelope(
            units.length_to_si(x_retracted),
            units.length_to_si(x_extended),
            units.length_to_si(y_retracted),
            minimum_angle,
            minimum_stages,
            maximum_stages,
        )
        if not candidates:
            st.warning("No candidate in the selected stage range satisfies this envelope and minimum angle.")
        else:
            display_rows = []
            for row in candidates:
                display_rows.append(
                    {
                        "Stages": int(row["stages"]),
                        f"Link length ({units.length})": units.length_from_si(row["link_length_mm"]),
                        "Retracted angle (°)": row["retracted_angle_deg"],
                        "Extended angle (°)": row["extended_angle_deg"],
                        f"Extended height ({units.length})": units.length_from_si(row["extended_height_mm"]),
                        "Expansion ratio": row["expansion_ratio"],
                    }
                )
            table = pd.DataFrame(display_rows).round(2)
            st.dataframe(table, use_container_width=True, hide_index=True)
            chosen = st.select_slider(
                "Preview candidate stage count",
                options=[int(row["stages"]) for row in candidates],
                key=f"env_preview_{unit_key}",
            )
            chosen_row = next(row for row in candidates if int(row["stages"]) == chosen)
            fig = lazy_tong_figure(chosen, chosen_row["extended_angle_deg"])
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.caption("Candidates satisfy the ideal pivot envelope; allow additional clearance for link width, joints, stops, and manufacturing tolerances.")
    except ValueError as exc:
        st.error(str(exc))

with capacity_tab:
    st.write(
        "Screen one loaded configuration. The result is the minimum of idealized link yielding, weak-axis Euler buckling, pin shear, and link bearing capacities."
    )
    load_angle = st.slider(
        "Loaded link angle (degrees)", 5.0, 80.0, 20.0, 1.0, key=f"cap_angle_{unit_key}"
    )
    orientation = st.radio(
        "Extension-axis orientation",
        ["Vertical", "Horizontal or other"],
        horizontal=True,
        key=f"cap_orientation_{unit_key}",
    )
    design_load = number(
        f"Required axial output load ({units.force})",
        default(units, 1000.0, 225.0),
        key=f"cap_design_load_{unit_key}",
        minimum=0.01,
        step=default(units, 100.0, 25.0),
        help_text="For a vertical linkage this can represent payload weight. A horizontal tip load is outside the axial model.",
    )
    dimensions, materials, joints = st.columns(3, gap="large")
    with dimensions:
        st.markdown("**Link geometry**")
        cap_l = number(f"Link length ({units.length})", default(units, 250.0, 10.0), key=f"cap_L_{unit_key}", minimum=0.01, step=default(units, 5.0, 0.1))
        cap_b = number(f"Link width ({units.length})", default(units, 25.0, 1.0), key=f"cap_b_{unit_key}", minimum=0.01, step=default(units, 1.0, 0.05))
        cap_t = number(f"Link thickness ({units.length})", default(units, 4.0, 0.16), key=f"cap_t_{unit_key}", minimum=0.01, step=default(units, 0.5, 0.01))
    with materials:
        st.markdown("**Link properties**")
        cap_sy = number(f"Link yield strength ({units.stress})", default(units, 250.0, 36.0), key=f"cap_sy_{unit_key}", minimum=0.01, step=default(units, 10.0, 1.0))
        cap_e = number(f"Elastic modulus ({units.modulus})", default(units, 200.0, 29.0), key=f"cap_e_{unit_key}", minimum=0.01, step=default(units, 5.0, 1.0))
        cap_k = number("Effective-length factor, K", 1.0, key=f"cap_k_{unit_key}", minimum=0.1, step=0.1)
    with joints:
        st.markdown("**Joint checks**")
        cap_d = number(f"Pivot diameter ({units.length})", default(units, 6.0, 0.25), key=f"cap_d_{unit_key}", minimum=0.01, step=default(units, 0.5, 0.01))
        cap_pin_sy = number(f"Pin yield strength ({units.stress})", default(units, 400.0, 58.0), key=f"cap_pin_sy_{unit_key}", minimum=0.01, step=default(units, 10.0, 1.0))
        cap_bearing = number(f"Bearing limit stress before FOS ({units.stress})", default(units, 200.0, 29.0), key=f"cap_bear_{unit_key}", minimum=0.01, step=default(units, 10.0, 1.0))
        cap_planes = st.radio("Pin shear planes", [1, 2], horizontal=True, index=1, key=f"cap_planes_{unit_key}")
    cap_fos = number("Design factor of safety", 2.0, key=f"cap_fos_{unit_key}", minimum=1.0, step=0.1)

    try:
        cap = preliminary_capacity(
            angle_deg=load_angle,
            link_length_mm=units.length_to_si(cap_l),
            link_width_mm=units.length_to_si(cap_b),
            link_thickness_mm=units.length_to_si(cap_t),
            link_yield_mpa=units.stress_to_si(cap_sy),
            elastic_modulus_gpa=units.modulus_to_si(cap_e),
            effective_length_factor=cap_k,
            pin_diameter_mm=units.length_to_si(cap_d),
            pin_yield_mpa=units.stress_to_si(cap_pin_sy),
            pin_shear_planes=cap_planes,
            bearing_allowable_mpa=units.stress_to_si(cap_bearing),
            factor_of_safety=cap_fos,
        )
        force = units.force_from_si(cap.output_capacity_n)
        target_si = units.force_to_si(design_load)
        margin = cap.output_capacity_n / target_si
        c1, c2, c3 = st.columns(3)
        c1.metric("Estimated axial capacity", f"{force:,.1f} {units.force}")
        c2.metric("Governing screen", cap.governing_mode)
        c3.metric("Capacity / required load", f"{margin:.2f}")
        status_box(
            margin >= 1.0,
            "The required axial load passes all included screening checks.",
            "The required axial load exceeds at least one included screening capacity.",
        )
        if orientation == "Vertical":
            if units.is_si:
                st.metric("Equivalent supported mass", f"{cap.output_capacity_n / 9.80665:,.1f} kg")
            else:
                st.metric("Equivalent supported weight", f"{force:,.1f} lbf")
        else:
            st.info("A horizontal tip payload creates bending and out-of-plane stability demands. This axial model therefore does not report a maximum supported weight for that orientation.")
        capacity_rows = {
            "Link yielding": cap.link_yield_capacity_n,
            "Link buckling": cap.link_buckling_capacity_n,
            "Pin shear": cap.pin_shear_capacity_n,
            "Link bearing": cap.bearing_capacity_n,
        }
        chart_data = pd.DataFrame(
            {"Mode": list(capacity_rows), "Capacity": [units.force_from_si(v) for v in capacity_rows.values()]}
        ).set_index("Mode")
        st.bar_chart(chart_data, color="#2D7FF9")
    except ValueError as exc:
        st.error(str(exc))

    with st.expander("What this capacity does—and does not—mean"):
        st.markdown(
            """
The two-force-member estimate uses N_link = P/(2 cos θ). Link yielding uses
SyA/FOS. Euler buckling uses π²EI/(KL)²/FOS about the weaker rectangular axis.
Pin shear uses the von Mises estimate τy = Sy/√3, and bearing uses projected
area dt. The displayed axial capacity is the smallest corresponding output.

It does **not** include joint tear-out, pin bending, actuator attachment loads,
friction, clearance, dynamic loading, fatigue, out-of-plane buckling, or
horizontal cantilever bending. Actuator force is not reported because it depends
on where and how the actuator is attached. Near-flat and near-folded
configurations also need special attention to transmission, interference, and
internal force.
"""
        )

with st.expander("Sources and verification trail"):
    st.markdown(
        """
- [Liao, Y. and Krishnan, S., “Deployable Scissor Structures: Classification of Modifications and Applications,” *Automation in Construction*, Vol. 165, 2024](https://experts.illinois.edu/en/publications/deployable-scissor-structures-classification-of-modifications-and/) (scissor-unit terminology, variations, and applications).
- [Budynas, R. G. and Nisbett, J. K., *Shigley’s Mechanical Engineering Design*, McGraw Hill](https://www.mheducation.com/highered/product/shigleys-mechanical-engineering-design-nisbett) (Euler buckling, pin shear, and bearing-stress design checks).

The geometry relation is derived directly from the horizontal and vertical projections of one full link. Strength outputs are screening estimates and should be independently checked before hardware is built.
"""
    )
