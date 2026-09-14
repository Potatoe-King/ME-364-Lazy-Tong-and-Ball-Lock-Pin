"""Clean, schematic-only mechanism drawings for the Streamlit interface."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle


NAVY = "#17324D"
BLUE = "#2D7FF9"
TEAL = "#00A6A6"
GOLD = "#F3B61F"
PALE = "#EDF3F7"
INK = "#1D2733"


def lazy_tong_figure(stages: int, angle_deg: float):
    """Draw a normalized lazy-tong mechanism at one angle."""
    theta = math.radians(angle_deg)
    dx = math.cos(theta)
    height = math.sin(theta)
    fig, ax = plt.subplots(figsize=(8.2, 2.8), dpi=140)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for i in range(stages):
        x0, x1 = i * dx, (i + 1) * dx
        ax.plot([x0, x1], [0, height], color=BLUE, lw=6, solid_capstyle="round")
        ax.plot([x0, x1], [height, 0], color=TEAL, lw=6, solid_capstyle="round")
        ax.add_patch(Circle(((x0 + x1) / 2, height / 2), 0.035, color=GOLD, zorder=5))

    for i in range(stages + 1):
        x = i * dx
        for y in (0, height):
            ax.add_patch(Circle((x, y), 0.044, facecolor="white", edgecolor=NAVY, lw=2.0, zorder=6))

    ax.plot([-0.08, -0.08], [-0.12, height + 0.12], color=NAVY, lw=4)
    ax.plot([stages * dx + 0.08, stages * dx + 0.08], [-0.12, height + 0.12], color=NAVY, lw=4)
    ax.set_xlim(-0.28, stages * dx + 0.28)
    ax.set_ylim(-0.28, max(0.55, height + 0.28))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    return fig


def ball_lock_figure(button_pressed: bool, insertion: float):
    """Draw a stylized section view of a ball-lock pin and a three-plate joint."""
    insertion = min(1.0, max(0.0, insertion))
    fig, ax = plt.subplots(figsize=(8.2, 2.8), dpi=140)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Joint plates and aligned holes.
    for x, width in ((4.0, 0.55), (5.0, 0.95), (6.35, 0.55)):
        ax.add_patch(Rectangle((x, -1.05), width, 2.1, facecolor=PALE, edgecolor=NAVY, lw=1.8))
        ax.add_patch(Rectangle((x - 0.02, -0.25), width + 0.04, 0.5, facecolor="white", edgecolor="none"))

    pin_x = 0.55 + 3.0 * insertion
    # Handle.
    ax.add_patch(
        FancyBboxPatch(
            (pin_x - 0.65, -0.62),
            1.0,
            1.24,
            boxstyle="round,pad=0.07,rounding_size=0.22",
            facecolor=NAVY,
            edgecolor=NAVY,
        )
    )
    # Shank and nose.
    ax.add_patch(Rectangle((pin_x + 0.28, -0.22), 4.7, 0.44, facecolor=BLUE, edgecolor=NAVY, lw=1.5))
    ax.add_patch(Circle((pin_x + 4.98, 0), 0.22, facecolor=BLUE, edgecolor=NAVY, lw=1.5))
    # Release button / plunger.
    button_offset = 0.16 if button_pressed else 0.0
    ax.add_patch(
        FancyBboxPatch(
            (pin_x - 0.36 + button_offset, -0.18),
            0.34,
            0.36,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=GOLD,
            edgecolor=NAVY,
            lw=1.3,
        )
    )
    ax.plot([pin_x - 0.02 + button_offset, pin_x + 4.12], [0, 0], color=GOLD, lw=3.2)

    ball_radius = 0.105
    ball_y = 0.08 if button_pressed else 0.235
    ball_x = pin_x + 4.17
    for sign in (-1, 1):
        ax.add_patch(
            Circle(
                (ball_x, sign * ball_y),
                ball_radius,
                facecolor=TEAL,
                edgecolor=NAVY,
                lw=1.2,
                zorder=5,
            )
        )

    ax.set_xlim(-0.35, 8.5)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    return fig

