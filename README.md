# ME 36400 Mechanism Design Tools

This Streamlit package contains two interactive educational design aids:

1. **Lazy-Tong Designer** — explore motion, solve one unknown in the ideal geometry, search integer-stage configurations that fit a target envelope, and screen an axially loaded linkage for yielding, Euler buckling, pivot shear, and link bearing.
2. **Ball-Lock Pin Selector** — animate locking and release, size a pin body for transverse shear and member bearing, calculate minimum grip length, check an existing selection, and verify axial retention against manufacturer data.

The tools support both SI and US customary inputs. Calculations are converted to N, mm, MPa, and GPa internally.

## Run the app

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

The terminal prints a local URL, normally `http://localhost:8501`. Keep the terminal open while using the app.

## Suggested class-library format

Submit the project as an **interactive Python/Streamlit design tool**. A reviewer can work through both devices in roughly 8–12 minutes. The assumed prior knowledge is introductory statics, stress, factors of safety, and trigonometry.

For a hosted version, put this folder in a GitHub repository and deploy `app.py` as the main file through Streamlit Community Cloud. Also keep the zipped source folder with the submission so the calculation logic remains inspectable.

## What the models mean

### Lazy tong

For `n` complete symmetric stages made from links of full pivot-to-pivot length `L` at angle `theta` to the extension axis:

- axial length: `x = n L cos(theta)`
- pivot-to-pivot stage height: `y = L sin(theta)`
- ideal input force for an actuator that directly changes the common stage height `y`: `F_in = P n tan(theta)`; other attachment geometries require their own virtual-work relationship
- ideal axial force in each of the two end links: `N_link = P / [2 cos(theta)]`

The envelope search interprets the retracted height as an exact pivot-to-pivot height, not the outside hardware profile. Real designs need added space for link width, overlapping layers, fasteners, stops, and clearance.

The capacity tab is a preliminary, centered, in-plane axial screen. It compares link yielding, weak-axis Euler buckling, pivot shear, and link bearing, reports the maximum screened capacity, and compares it with a required axial load. It does not cover actuator attachment loads, tear-out, pin bending, joint clearance, friction, dynamics, fatigue, out-of-plane instability, or horizontal cantilever loading. The app only reports a supported mass/weight when the extension axis is vertical.

### Ball-lock pin

The transverse screen treats the shank as a pin in one or two shear planes. User-entered yield and bearing-limit stresses are divided by the selected design factor:

- uniform pin shear: `tau = F / (m A)`
- ductile shear-yield estimate: `tau_y = Sy / sqrt(3)`
- projected bearing stress: `p = F / (t d)` for the center member; in a symmetric double-shear clevis each outer lug carries `F/2`
- minimum grip: assembled stack plus the selected allowance

Ball pull-out is deliberately not calculated from ball geometry. It depends on the exact manufactured pin assembly and receiving-hole geometry, so the app requires the user to enter a rating from the selected manufacturer's technical data. The rating-definition control distinguishes an allowable catalog value from an ultimate/failure value to avoid applying the factor of safety twice.

## Validate the calculation engine

No extra testing package is required:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

The test suite covers geometry, inverse solutions, integer stage rounding, envelope reconstruction, capacity-governing logic, double-shear stress, standard-size rounding, and axial-rating treatment.

## Sources

- Yuan Liao and Sudarshan Krishnan, “Deployable Scissor Structures: Classification of Modifications and Applications,” *Automation in Construction*, Vol. 165, 2024: https://experts.illinois.edu/en/publications/deployable-scissor-structures-classification-of-modifications-and/
- Carr Lane Manufacturing, “Anatomy of a Ball Lock Pin: Components, Mechanism & Operation”: https://www.carrlane.com/engineering-resources/technical-information/ball-lock-pins-engineering-application/how-ball-lock-pins-work
- Carr Lane Manufacturing, “Ball Lock Pin Technical Information,” including approximate pull-out and calculated double-shear strengths: https://www.carrlane.com/engineering-resources/technical-information/manual-workholding/ball-lock-pin-technical-information
- Richard G. Budynas and J. Keith Nisbett, *Shigley’s Mechanical Engineering Design*, McGraw Hill: https://www.mheducation.com/highered/product/shigleys-mechanical-engineering-design-nisbett

## AI disclosure

ChatGPT/Codex was used to help plan the app, draft Python code, create the schematic visualizations, organize the interface, and construct calculation tests. Engineering relationships and limitations were checked against the sources above. The app explicitly requires manufacturer data where a general analytical model would be misleading.
