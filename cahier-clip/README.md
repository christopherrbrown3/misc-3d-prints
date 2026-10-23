# Cahier clip

A one-piece spring clip that marks a page in a pocket Moleskine Cahier
(3.5 × 5.5 in / 90 × 140 mm). It slides over the page block from the top edge:
a long bottom plate sits behind the pages, a shorter tongue presses on top,
and the bridge between them provides the spring. The tongue tip has a lead-in
ramp so it wedges over pages instead of snagging. "CRB" is engraved into the
top of the tongue.

![Cahier clip v1](v1/preview.png)

## Versions

| Version | Status |
| --- | --- |
| [V1](v1/) | Modeled in SolidCraft 0.16.1; mesh verified watertight. Not yet printed — grip and flex are unverified. |

## Dimensions

| Feature | Dimension |
| --- | --- |
| Overall envelope | 44 × 30 × 2.9 mm |
| Bottom plate | 44 mm deep |
| Tongue | 37 mm deep, lead-in ramp over the last 4 mm |
| Wall thickness | 0.9 mm |
| Grip gap | 1.1 mm |
| Edge fillets | 0.6 mm on the bridge corners and tongue tip |
| Monogram | "CRB", 7 mm cap height, engraved 0.35 mm |

The 1.1 mm gap is sized to grip the back cover plus a few pages, or a modest
page stack on its own. Whether PETG at 0.9 mm gives the right spring — firm
enough to stay put in a back pocket, gentle enough not to crease pages — is
the open question for the first print.

## Printing

Target printer is a Bambu Lab A1 with a 0.4 mm nozzle:

- PETG (PLA will fatigue where the bridge flexes).
- Print flat, large face down, so the bridge bends within the layer planes.
- At 0.9 mm the walls are effectively solid at two perimeters; infill is
  irrelevant.
- Roughly 10 minutes and 3 g of filament.

## Files

- `source/build_v1.py` — drives SolidCraft's MCP server to rebuild the part.
- `source/cahier-clip.solidcraft` — the editable SolidCraft design.
- `v1/cahier-clip.stl` — millimeter STL, watertight, single solid.
- `v1/mesh_check.json` — measured dimensions and volume for the STL.
- `v1/preview.png` — render from SolidCraft.

Iteration knobs, all in the build script's profile sketch: grip gap, tongue
length, width, wall thickness, and the monogram text.
