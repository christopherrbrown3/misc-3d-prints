from pathlib import Path
import sys
SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE))
from geometry import *
TARGET = SOURCE.parent / 'v2'
TARGET.mkdir(parents=True, exist_ok=True)
OUTREV = str(TARGET)

"""Second one-piece shelf: deeper integral rear heels oppose forward rotation.

Run after geometry.py in Blender. Coordinates are millimetres. Existing scenes
and the first printed design are preserved. The 24 mm heel reach is nominal,
based on the 22 mm hook throat and the installed photo; it is not a measurement.
"""
LEVEL = {
    'width': 190.0, 'depth': 112.0, 'deck': 6.0,
    'hook_spacing': 124.0, 'hook_width': 26.0,
    'hook_gap': 22.0, 'hook_return_thickness': 4.0,
    'hook_top': 82.0, 'hook_bridge': 8.0, 'hook_drop': 14.0,
    'rear_heel_reach': 24.0, 'rear_heel_width': 20.0,
    'rear_heel_height': 23.0, 'cable_bay': 35.0,
}

scene = new_scene('Roam level V2 | assembly')
w, d, t = LEVEL['width'], LEVEL['depth'], LEVEL['deck']
obj = box('LEVEL V2 | one-piece Roam shelf', -w/2, w/2, 0, d, 0, t)
parts = [box('V2 low front lip', -94, 94, 106, 112, 2, 11.5)]
for sign in (-1, 1):
    cx = sign*(w/2-2.5)
    parts.append(box('V2 low end lip', cx-2.5, cx+2.5, 38, 111, 2, 14))
    cx = sign*LEVEL['hook_spacing']/2
    gap = LEVEL['hook_gap']
    seat = LEVEL['hook_top']-LEVEL['hook_bridge']
    top = LEVEL['hook_top']
    back = gap+LEVEL['hook_return_thickness']
    hook_profile = [(6, 2), (6, top), (-back, top),
                    (-back, seat-LEVEL['hook_drop']),
                    (-gap, seat-LEVEL['hook_drop']), (-gap, seat),
                    (0, seat), (0, 2)]
    parts.append(prism_x('V2 integral hook', cx-13, cx+13, hook_profile))
    parts.append(prism_x('V2 front brace', cx-3.5, cx+3.5,
                         [(3, 2), (3, 63), (38, 2)]))
    # The rear heels reach toward the wall/set-back rail web. Their underside
    # stays on the build plate, so the added reach needs no underside support.
    reach = LEVEL['rear_heel_reach']
    half = LEVEL['rear_heel_width']/2
    height = LEVEL['rear_heel_height']
    heel = [(2, 0), (2, height+7), (-reach+2, height),
            (-reach, height-2), (-reach, 0)]
    parts.append(prism_x('V2 integral rear heel', cx-half, cx+half, heel))
    stop = sign*79
    parts.append(box('V2 rear speaker stop', stop-5, stop+5, 38, 41, 2, 12))
for part in parts:
    boolean(obj, part, 'UNION')
boolean(obj, bevel(box('V2 open cord exit', -8, 8, -2, 35, -2, 8), 1.8, 5),
        'DIFFERENCE')
bevel(obj, 0.8, 4)
finalize_mesh(obj)
mat = bpy.data.materials.get('One piece | charcoal PLA')
obj.data.materials.clear()
if mat is None:
    mat = material('Level V2 | charcoal PLA', (0.09, 0.10, 0.12))
if mat is not None:
    obj.data.materials.append(mat)
for face in obj.data.polygons:
    face.material_index = 0
obj['printable'] = True
obj['one_piece'] = True
obj['hardware'] = 'None'
obj['cable_clearance_mm'] = LEVEL['cable_bay']
obj['nominal_hook_gap_mm'] = LEVEL['hook_gap']
obj['rear_heel_reach_mm'] = LEVEL['rear_heel_reach']
obj['revision'] = 'V2: 24 mm integral rear heels replace 4 mm rear pads'
obj['print_orientation'] = 'Deck and rear heels flat; tree supports under hooks'
scene['fit_note'] = 'Heel reach is nominal; verify seating on the real mount'

print_scene = new_scene('Roam level V2 | print orientation')
print_obj = duplicate(obj, 'PRINT | level V2 shelf', print_scene)
export_stl(print_obj, OUTREV+'/roam_shelf_level_v2.stl')
print(json.dumps(geometry_report(print_obj)))
bpy.context.window.scene = scene

original = bpy.data.scenes.get('Roam one piece | assembly')
if original is not None:
    scene.world = original.world
    for ref in original.objects:
        if ref.name.startswith('ONE PIECE REF |') or ref.type in {'CAMERA', 'LIGHT'}:
            other = duplicate(ref, 'LEVEL V2 REF | '+ref.name, scene)
            other['printable'] = False
            if ref.type in {'CAMERA', 'LIGHT'}:
                other.hide_set(True)
            if ref == original.camera:
                scene.camera = other
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        if scene.camera is not None:
            area.spaces.active.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
        area.spaces.active.region_3d.view_location = Vector((0, 35, 30))
        area.spaces.active.region_3d.view_distance = 320
        area.spaces.active.overlay.show_overlays = False
activate(obj)
print('V2: same hooks and cable clearance; deeper rear heels oppose rotation.')

bpy.ops.wm.save_as_mainfile(filepath=str(TARGET/'generated_v2.blend'),
                             check_existing=False, copy=True, compress=True)
