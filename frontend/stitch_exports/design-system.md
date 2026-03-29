# Design System: Prague Fiscal Ledger

```markdown
# Design System Strategy: The Administrative Architect

## 1. Overview & Creative North Star
The "Creative North Star" for this system is **The Administrative Architect**. In the world of Czech taxation (*Daně*), reliability isn't just a feature—it is the foundation. This system moves away from the chaotic, cluttered spreadsheets of traditional tax software and toward a high-end, editorial experience that feels like a premium law firm’s digital dossier.

Instead of a "web app" feel, we are building a "Digital Document." We break the standard grid-bound template look by using **intentional asymmetry** (e.g., wide margins on the left for navigation, dense data on the right) and **tonal depth**. We treat the UI as a series of sophisticated, stacked vellum sheets where information is revealed through hierarchy, not borders.

---

## 2. Colors: The Palette of Authority
The color strategy avoids "tech blue" in favor of `primary: #001f3c` (Prussian Blue), evoking the ink of official stamps and high-end stationery.

*   **The "No-Line" Rule:** 1px solid borders are strictly prohibited for sectioning. To separate the personal info section from the income section, transition from `surface` (#f8f9fa) to `surface_container_low` (#f3f4f5). 
*   **Surface Hierarchy & Nesting:** Use a "Physical Stacking" logic. The base page is `surface`. A main calculation module should sit on `surface_container`. Within that module, individual data cards must use `surface_container_lowest` (#ffffff) to appear as though they are "floating" sheets of paper on a desk.
*   **The "Glass & Gradient" Rule:** For the "Tax Refund/Liability" summary (the most critical data), use a semi-transparent `surface_tint` with a `backdrop-blur` of 12px.
*   **Signature Textures:** For the "Submit" area, use a subtle linear gradient from `primary` (#001f3c) to `primary_container` (#003460). This adds a "weighted" feel to the final action, signifying the importance of the submission.

---

## 3. Typography: The Editorial Record
We use a dual-font system to balance the "Official Document" look with modern readability.

*   **Public Sans (Display/Headline):** Used for `display-lg` through `headline-sm`. Its neutral, geometric sturdiness mimics the clarity of a government header.
*   **Work Sans (Title/Body/Label):** Used for everything else. It has a slightly more "human" feel than a standard grotesque, ensuring that long tax explanations don't feel fatiguing.

**Hierarchy as Identity:**
- **The "Hero" Figure:** Use `display-md` (2.75rem) for the final tax amount. It should be the largest element on the screen, commanding total attention.
- **The "Official Note":** Use `label-md` in `on_surface_variant` (#43474f) for legal disclaimers, mimicking the "fine print" of a physical *Daňové přiznání*.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too "tech." We use light to create professional gravitas.

*   **The Layering Principle:** Depth is achieved by stacking. A `surface_container_highest` (#e1e3e4) sidebar against a `surface` (#f8f9fa) body provides all the separation needed.
*   **Ambient Shadows:** If a modal is required (e.g., for adding a dependent), use a shadow with a 40px blur at 6% opacity. The shadow color should be a tinted `#001c38` (on_primary_fixed) to feel like a natural shadow cast by deep blue ink.
*   **The "Ghost Border" Fallback:** If accessibility requires a stroke (e.g., high-contrast mode), use `outline_variant` (#c3c6d1) at **15% opacity**. It should be barely felt, only sensed.

---

## 5. Components: The Tax Ledger

*   **Input Fields:** Eschew the box. Use a "Minimal Ledger" style: a `surface_container_high` background with a `0.25rem` (DEFAULT) roundedness. No border. Upon focus, the background shifts to `surface_container_lowest` with a subtle `primary` underline (2px).
*   **Buttons:**
    *   *Primary:* `primary` (#001f3c) background, `on_primary` (#ffffff) text. Use `xl` (0.75rem) roundedness for a modern, approachable feel.
    *   *Secondary:* `secondary_container` background. No border.
*   **Cards:** Forbid divider lines. Use `spacing.8` (1.75rem) of vertical white space to separate the "Employer" section from the "Deductions" section.
*   **The "Output" Card:** For the final document preview, use `surface_container_lowest` with a "Ghost Border." This represents the physical paper of the *Danove priznani*.
*   **Progress Stepper:** Use `surface_container_highest` for inactive steps and `primary` for the active step. Connect them with a wide `primary_fixed` bar, not a thin line.

---

## 6. Do’s and Don’ts

### Do:
*   **Use High Contrast for Values:** The currency values (CZK) should always be in `primary` or `tertiary` (if an error) to ensure they are the first thing the eye sees.
*   **Embrace Negative Space:** Tax forms are usually cramped. Break the mold. Use `spacing.16` (3.5rem) to separate major logical blocks.
*   **Align to the Typeface:** Use the `publicSans` display scale for all numerical summaries to maintain the "Architectural" feel.

### Don’t:
*   **No "Safety Orange":** Use `tertiary` (#381300) or `error` (#ba1a1a) for warnings. Avoid generic orange; it looks like a construction app, not a tax app.
*   **No Heavy Dividers:** Never use a 100% opaque line to separate content. It clutters the interface and makes it look like an old-fashioned table.
*   **No Standard Shadows:** Avoid the "CSS default" shadow look. If it looks like a 2015 Material Design app, it has failed the premium editorial requirement.
```
