##############################################################################
#                                                                            #
#   Three examples of using the Enumerator Property in Blender 3.3           #
#                          Pan Thistle, 2023                                 #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU General Public License as published by     #
#   the Free Software Foundation, either version 3 of the License, or        #
#   (at your option) any later version.                                      #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU General Public License for more details.                             #
#                                                                            #
#   You should have received a copy of the GNU General Public License        #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
#                                                                            #
##############################################################################


import bpy
import math
import bmesh

from mathutils import Vector


# RUN THIS MODULE ONCE TO CREATE THE OBJECTS REQUIRED FOR THE "enum_ex3b" DEMO


def new_mesh_object(name, coll, vcs, fcs):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(use_operators=False)
    bmvs = [bm.verts.new(v) for v in vcs]
    for f in fcs:
        bm.faces.new((bmvs[i] for i in f))
    bm.to_mesh(me)
    me.update()
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


# demo collection ----------------------------------------

name = "base_objects"
if name in bpy.data.collections:
    coll = bpy.data.collections[name]
else:
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)


# point object -------------------------------------------


def pnt_object(name, coll):
    r = 0.0625
    vcs = [
        (-r, -r, -r),
        (r, -r, -r),
        (r, -r, r),
        (-r, -r, r),
        (-r, r, r),
        (-r, r, -r),
        (r, r, r),
        (r, r, -r),
    ]
    fcs = [
        (0, 1, 2, 3),
        (0, 3, 4, 5),
        (3, 2, 6, 4),
        (0, 5, 7, 1),
        (1, 7, 6, 2),
        (6, 7, 5, 4),
    ]
    return new_mesh_object(name, coll, vcs, fcs)


pob = pnt_object("pob", coll)


# vec object ---------------------------------------------


def vec_object(name, coll):
    r = 0.006
    n = 8
    t = 0.25 * math.pi  # math.radians(360/8)
    vcs = [Vector((r * math.cos(t * i), 0, r * math.sin(t * i))) for i in range(n)]
    y = Vector((0, 1, 0))
    vcs = vcs + [v + y for v in vcs]
    scan = list(range(n)) + [0] + list(range(n, n * 2)) + [n]
    fcs = [[scan[i], scan[i + n + 1], scan[i + n + 2], scan[i + 1]] for i in range(n)]
    return new_mesh_object(name, coll, vcs, fcs)


vob = vec_object("vob", coll)
