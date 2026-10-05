"""Shared Blender mesh utilities. Coordinates are millimeters."""

import bpy

import bmesh

import math

import json

from mathutils import Vector, Matrix

def enum(obj, key, value):
    values = [i.identifier for i in obj.bl_rna.properties[key].enum_items]
    if value not in values:
        raise ValueError((key, value, values))
    return value

def activate(obj):
    bpy.context.view_layer.update()
    for other in list(bpy.context.view_layer.objects):
        if other is not None and other.select_get():
            other.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def new_scene(name):
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    scene.unit_settings.system = enum(scene.unit_settings, 'system', 'METRIC')
    scene.unit_settings.scale_length = 0.001
    return scene

def mesh(name, vertices, faces):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return obj

def box(name, x0, x1, y0, y1, z0, z1):
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh(name, v, f)

def prism_x(name, x0, x1, yz):
    n = len(yz)
    v = [(x0,y,z) for y,z in yz] + [(x1,y,z) for y,z in yz]
    f = [tuple(range(n-1,-1,-1)), tuple(range(n,n*2))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name, v, f)

def prism_y(name, y0, y1, xz):
    n = len(xz)
    v = [(x,y0,z) for x,z in xz] + [(x,y1,z) for x,z in xz]
    f = [tuple(range(n-1,-1,-1)), tuple(range(n,n*2))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name, v, f)

def bevel(obj, width, segments=3):
    activate(obj)
    mod = obj.modifiers.new('Soft edges', 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = enum(mod, 'limit_method', 'ANGLE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def boolean(obj, other, operation):
    activate(obj)
    mod = obj.modifiers.new(operation, 'BOOLEAN')
    mod.operation = enum(mod, 'operation', operation)
    mod.solver = enum(mod, 'solver', 'EXACT')
    mod.object = other
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(other, do_unlink=True)
    bpy.context.view_layer.update()
    return obj

def material(name, colour, metallic=0.0, roughness=0.55):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*colour,1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = (*colour,1)
    return mat

def duplicate(obj, name, scene=None):
    other = obj.copy()
    other.data = obj.data.copy()
    other.name = name
    (scene or bpy.context.scene).collection.objects.link(other)
    return other

def export_stl(obj, path):
    activate(obj)
    bpy.ops.wm.stl_export(filepath=path,export_selected_objects=True,
                          global_scale=1.0,use_scene_unit=False,apply_modifiers=True)

def geometry_report(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    report = {'object': obj.name, 'vertices': len(bm.verts), 'faces': len(bm.faces),
              'non_manifold_edges': sum(not e.is_manifold for e in bm.edges),
              'volume_mm3': bm.calc_volume(signed=True)}
    bm.free()
    return report

def finalize_mesh(obj):
    # Booleans and bevels can leave edges below STL float32 precision. Remove
    # those before triangulation so the exported solid keeps the same topology.
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj
