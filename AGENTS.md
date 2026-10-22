# Poly Shell UI requirements

The user requires every UI change to work with all visual themes and future themes.
Use the live semantic palette from Session / theme/Theme.qml for surfaces, text,
icons, strokes and accents, including Timeline's intermediate palettes. Never bake
Alpine's sage colors or a reference image's purple colors into components. Preserve
Work/Vibe mode independence, configured geometry, reduced motion and real device
states. Follow docs/theme-design-contract.md.

The approved hover design is assets/reference/hover-faceted-approved.png. Keep the
hover menu compact and separate from the full control center. Open and begin closing
without timed hover delays; preserve pointer access across the gap to the bar.

Latest hover refinement: show Wi-Fi strength only through its status icon, keep
the three status cards compact, and use the shared configured panelRadius for
rounded surfaces. The user rejected bevelled/sharp hover corners.

The user subsequently requested matching the actual full quick-control panel.
Reuse its QuickSwitchTile, ControlRow and QuickActionButton components in the
hover view; do not introduce separate visual styling for these controls.
