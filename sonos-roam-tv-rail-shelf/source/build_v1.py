from pathlib import Path
import sys
SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE))
from geometry import *
TARGET = SOURCE.parent / 'v1'
TARGET.mkdir(parents=True, exist_ok=True)
OUTPUT = str(TARGET)

"""One continuous shelf with two roomy, integral gravity hooks. No fasteners.

Coordinates are millimetres. The 22 mm nominal throat is a generous design
assumption for exposed hanging lips, not a claim that all mounts share a size.
"""
ONE = {
    'width':190.0, 'depth':112.0, 'deck':6.0,
    'hook_spacing':124.0, 'hook_width':26.0, 'stem_thickness':6.0,
    'hook_gap':22.0, 'hook_return_thickness':4.0,
    'hook_top':82.0, 'hook_bridge':8.0, 'hook_drop':14.0,
    'cable_bay':35.0,
}

scene = new_scene('Roam one piece | assembly')
w,d,t=ONE['width'],ONE['depth'],ONE['deck']
obj=box('ONE PIECE | Roam hanging shelf',-w/2,w/2,0,d,0,t)
parts=[box('low front lip',-94,94,106,112,2,11.5)]
for sign in (-1,1):
    cx=sign*(w/2-2.5)
    parts.append(box('low end lip',cx-2.5,cx+2.5,38,111,2,14))
    cx=sign*ONE['hook_spacing']/2
    gap=ONE['hook_gap']
    return_wall=ONE['hook_return_thickness']
    top=ONE['hook_top']
    seat=top-ONE['hook_bridge']
    profile=[(6,2),(6,top),(-gap-return_wall,top),
             (-gap-return_wall,seat-ONE['hook_drop']),
             (-gap,seat-ONE['hook_drop']),(-gap,seat),(0,seat),(0,2)]
    parts.append(prism_x('integral hook',cx-13,cx+13,profile))
    parts.append(prism_x('integral brace',cx-3.5,cx+3.5,[(3,2),(3,63),(38,2)]))
    # Integral rear contact pads reduce rocking against the front of the rail.
    parts.append(box('rear contact pad',cx-9,cx+9,-4,2,9,23))
    stop=sign*79
    parts.append(box('rear speaker stop',stop-5,stop+5,38,41,2,12))
for part in parts:
    boolean(obj,part,'UNION')
boolean(obj,bevel(box('open cord exit',-8,8,-2,35,-2,8),1.8,5),'DIFFERENCE')
bevel(obj,0.8,4)
finalize_mesh(obj)
obj.data.materials.clear()
obj.data.materials.append(material('One piece | charcoal PLA',(0.09,0.10,0.12)))
for face in obj.data.polygons:
    face.material_index=0
obj['printable']=True
obj['one_piece']=True
obj['hardware']='None'
obj['cable_clearance_mm']=35.0
obj['nominal_hook_gap_mm']=22.0
obj['print_orientation']='Deck flat; tree supports under the two hook overhangs'
obj['fit_note']='Loose fit over an exposed upper rail lip. Not every mount profile is compatible.'
scene['status']='V1 printed and fitted; forward tilt reported; no formal load rating'
scene['research']='SANUS VLL5 and Monoprice SlimSelect installation drawings'

print_scene=new_scene('Roam one piece | print orientation')
print_obj=duplicate(obj,'PRINT | one-piece shelf',print_scene)
export_stl(print_obj,OUTPUT+'/roam_shelf_one_piece.stl')
print(json.dumps(geometry_report(print_obj)))
bpy.context.window.scene=scene


bpy.ops.wm.save_as_mainfile(filepath=str(TARGET/'generated_v1.blend'),
                             check_existing=False, copy=True, compress=True)
