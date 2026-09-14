# Cover Card

| Field | Entry |
|---|---|
| Name and last two digits of PUID | **[Add your information]** |
| Device 1 | **5 — Lazy-tong expanding linkage** |
| Device 2 | **63 — Ball-detent quick-release pin** |
| Format of this package | Interactive Python/Streamlit design tool with two device pages |
| Approximate time to work through | 8–12 minutes |
| Assumed prior knowledge | Introductory statics, stress, factors of safety, and trigonometry |
| AI disclosure | ChatGPT/Codex assisted with app planning, Python implementation, schematic visualizations, interface organization, and calculation tests. Engineering claims and limits were checked against the listed sources. |

## Three self-check questions and answers

1. **For a lazy tong with fixed stage count and link length, what happens to its axial length when the link angle decreases?**  
   The axial length increases because `x = n L cos(theta)` and the cosine increases as an acute angle decreases.

2. **Why can the lazy-tong app report a supported weight for a vertical extension but not for a horizontal tip load?**  
   A vertical payload can be treated as an axial output load in the simplified model. A horizontal tip load creates bending and out-of-plane stability demands that the axial screen does not represent.

3. **Why are diameter, grip length, and axial pull-out rating separate choices for a ball-lock pin?**  
   Diameter primarily controls transverse shear and member bearing; grip length must fit the assembled stack; and axial retention depends on the complete locking-ball assembly and receiving geometry, so it must come from exact manufacturer data.

## Sources

- Liao, Y. and Krishnan, S., “Deployable Scissor Structures: Classification of Modifications and Applications,” *Automation in Construction*, Vol. 165, 2024. https://experts.illinois.edu/en/publications/deployable-scissor-structures-classification-of-modifications-and/
- Carr Lane Manufacturing, “Anatomy of a Ball Lock Pin: Components, Mechanism & Operation.” https://www.carrlane.com/engineering-resources/technical-information/ball-lock-pins-engineering-application/how-ball-lock-pins-work
- Carr Lane Manufacturing, “Ball Lock Pin Technical Information.” https://www.carrlane.com/engineering-resources/technical-information/manual-workholding/ball-lock-pin-technical-information
- Budynas, R. G. and Nisbett, J. K., *Shigley’s Mechanical Engineering Design*, McGraw Hill. https://www.mheducation.com/highered/product/shigleys-mechanical-engineering-design-nisbett

