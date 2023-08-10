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


# Example 3b: Sync enum property with user-list. Object Rotations Demo.


import bpy
import uuid

from math import radians
from mathutils import Vector


# *** DEMO REQUIREMENT:
def req_check(scene):
    try:
        coll = scene.collection.children["base_objects"]
        ob = coll.objects["pob"]
        ob = coll.objects["vob"]
    except Exception:
        print("missing required objects")
        return False
    return True


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class PTDOBRELS_sub(bpy.types.PropertyGroup):
    def object_color_update(self, context):
        if self.pnt_ob:
            self.pnt_ob.color = self.object_color

    def object_scale_update(self, context):
        if self.pnt_ob:
            v = self.object_scale
            self.pnt_ob.scale = (v, v, v)

    name: bpy.props.StringProperty(default="sub")
    # viewport objects
    pnt_ob: bpy.props.PointerProperty(type=bpy.types.Object)
    object_color: bpy.props.FloatVectorProperty(
        name="Color",
        size=4,
        default=(0.186, 0.186, 0.186, 1),
        min=0,
        max=1,
        subtype="COLOR",
        update=object_color_update,
        options={"HIDDEN"},
    )
    object_scale: bpy.props.FloatProperty(
        name="Scale",
        default=1,
        min=0.1,
        max=10,
        update=object_scale_update,
        options={"HIDDEN"},
    )
    vec_ob: bpy.props.PointerProperty(type=bpy.types.Object)
    # ids
    uid: bpy.props.StringProperty(default="")
    pid: bpy.props.StringProperty(default="")
    # parent loc/rot
    ploc: bpy.props.FloatVectorProperty(
        size=3, default=[0, 0, 0], subtype="TRANSLATION"
    )
    prot: bpy.props.FloatVectorProperty(
        size=4, default=[1, 0, 0, 0], subtype="QUATERNION"
    )
    # calculations flag
    complete: bpy.props.BoolProperty(default=False)
    # location/rotation
    loc: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0], subtype="TRANSLATION")
    rot: bpy.props.FloatVectorProperty(
        size=4, default=[1, 0, 0, 0], subtype="QUATERNION"
    )
    # ui loc/rot input
    iloc: bpy.props.FloatVectorProperty(
        size=3, default=[0, 0, 0], subtype="TRANSLATION"
    )
    rotpiv: bpy.props.StringProperty(default="parent")
    rotang: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0], subtype="EULER")
    rotinf: bpy.props.BoolProperty(default=True)


class PTDOBRELS_props(bpy.types.PropertyGroup):
    def descendants(self, key, lst=[]):
        cids = [ob.uid for ob in self.subs if ob.pid == key]
        for cid in cids:
            lst.append(cid)
            # recursion
            lst = self.descendants(cid, lst)
        return lst

    def parent_enum_items(self, context):
        items = []
        if not bool(self.subs):
            return items
        idx = self.subs_idx
        key = self.subs[idx].uid
        dids = self.descendants(key, [])
        for i, item in enumerate(self.subs):
            if (i == idx) or (item.uid in dids):
                continue
            items.append((str(i), item.name, "", i))
        return items

    def parent_enum_update(self, context):
        self.p_idx = self.get("parent_enum", -1)

    def subs_idx_update(self, context):
        self.p_idx = -1
        if bool(self.subs):
            items = self.parent_enum_items(context)
            if bool(items):
                self.parent_enum = items[0][0]

    p_idx: bpy.props.IntProperty(default=-1)
    parent_enum: bpy.props.EnumProperty(
        name="Parent Links",
        description="parent",
        items=parent_enum_items,
        update=parent_enum_update,
        options={"HIDDEN"},
    )
    subs: bpy.props.CollectionProperty(type=PTDOBRELS_sub)
    subs_idx: bpy.props.IntProperty(
        name="sub", default=-1, update=subs_idx_update, options={"HIDDEN"}
    )


# ------------------------------------------------------------------------------
#
# --------------------- OBJECT RELATIONS FUNCTIONS -----------------------------


def update_sub_obs(item):
    # call from: 'update_sub'

    loc = item.loc
    ob = item.pnt_ob
    if ob:
        ob.hide_viewport = False
        ob.location = loc
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = item.rot.to_euler()
    else:
        print(f"{item.name} point object is missing!")

    ob = item.vec_ob
    if ob:
        ob.hide_viewport = False
        ob.location = item.ploc
        vdir = loc - item.ploc
        vrot = Vector((0, 1, 0)).rotation_difference(vdir)
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = vrot.to_euler()
        ob.scale[1] = vdir.length
    else:
        print(f"{item.name} vector object is missing!")


def finalize_sub(item):
    # call from: 'update_sub'

    ploc = item.ploc
    q = item.rotang.to_quaternion()
    rot = item.prot @ q
    loc = ploc + rot @ item.iloc if item.rotpiv == "parent" else ploc + item.iloc
    return loc, rot


def update_sub(props, item):
    # call from: 'scene_update'

    if item.complete:
        return
    if item.pid:
        p = None
        for i, pnt in enumerate(props.subs):
            if pnt.uid == item.pid:
                p = props.subs[i]
                break
        if p:
            if not p.complete:
                # *** recursion call ***#
                update_sub(props, p)
            # parent influence
            item.ploc = p.loc
            item.prot = p.rot if item.rotinf else (1, 0, 0, 0)
        else:
            print(f'{item.name} parent id: "{item.pid}" not found!')
            item.ploc = (0, 0, 0)
            item.prot = (1, 0, 0, 0)
    else:
        item.ploc = (0, 0, 0)
        item.prot = (1, 0, 0, 0)
    item.loc, item.rot = finalize_sub(item)
    # update display
    update_sub_obs(item)
    item.complete = True


def scene_update(scene):
    # call from: 'OT_sub_remove', 'OT_sub_parent', 'OT_sub'

    props = scene.ptdobrels_props
    # init state parameter
    for item in props.subs:
        item.complete = False
    # update objects
    for item in props.subs:
        if item.complete:
            continue
        update_sub(props, item)


def scene_update_frames(scene, val):
    props = scene.ptdobrels_props
    if not bool(props.subs):
        return
    # init state parameter and anim values
    if not val:
        for item in props.subs:
            item.complete = False
            item.rotang = (0, 0, 0)
    else:
        for i, item in enumerate(props.subs):
            item.complete = False
            if item.iloc[2]:
                item.rotang[1] = (i + 1) * val
            else:
                item.rotang[2] = (i + 1) * val
    # update objects
    for item in props.subs:
        if item.complete:
            continue
        update_sub(props, item)


# ------------------------------------------------------------------------------
#
# ----------------------------- OPERATORS --------------------------------------


class PTDOBRELS_OT_sub_add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "ptdobrels.sub_add"
    bl_description = "add sub system"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.ptdobrels_props
        return len(props.subs) < 20

    def execute(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        try:
            item = props.subs.add()
            item.uid = self.sub_uid_get()
            props.subs_idx = len(props.subs) - 1
            coll = scene.collection.children["base_objects"]
            item.pnt_ob = coll.objects["pob"].copy()
            item.pnt_ob.name = "obj"
            item.pnt_ob.location = (0, 0, 0)
            item.pnt_ob.hide_viewport = False
            scene.collection.objects.link(item.pnt_ob)
            item.vec_ob = coll.objects["vob"].copy()
            item.vec_ob.name = f"{item.pnt_ob.name}_vec"
            item.vec_ob.scale[1] = 0.01
            item.vec_ob.hide_viewport = False
            scene.collection.objects.link(item.vec_ob)
        except Exception as my_err:
            print(f"sub_add: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}

    def sub_uid_get(self):
        # make a UUID based on the host ID and current time
        # uuid.uuid1()
        # make a random UUID
        # uuid.uuid4()

        x = uuid.uuid4()
        return str(x)


class PTDOBRELS_OT_sub_remove(bpy.types.Operator):
    bl_label = "Remove"
    bl_idname = "ptdobrels.sub_remove"
    bl_description = "remove sub system"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = context.scene.ptdobrels_props
        return bool(props.subs)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        try:
            if self.doall:
                for item in props.subs:
                    self.remove_temps(scene, item)
                props.subs.clear()
                props.subs_idx = -1
                props.p_idx = -1
                return {"FINISHED"}
            idx = props.subs_idx
            item = props.subs[idx]
            self.remove_temps(scene, item)
            for b in props.subs:
                if b.pid == item.uid:
                    b.pid = item.pid
            props.subs.remove(idx)
            props.subs_idx = min(max(0, idx - 1), len(props.subs) - 1)
            if props.subs_idx < 0:
                props.p_idx = -1
                return {"FINISHED"}
            # scene updates
            scene_update(scene)
        except Exception as my_err:
            print(f"sub_remove: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}

    def remove_temps(self, scene, item):
        # remove linked copies

        ob = item.pnt_ob
        if ob:
            bpy.data.objects.remove(ob)
        ob = item.vec_ob
        if ob:
            bpy.data.objects.remove(ob)


class PTDOBRELS_OT_sub_parent(bpy.types.Operator):
    bl_label = "Set Parent"
    bl_idname = "ptdobrels.sub_parent"
    bl_description = "set parent system"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    val: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        try:
            item = props.subs[props.subs_idx]
            if not self.val:
                item.pid = ""
            else:
                p = props.subs[int(props.parent_enum)]
                item.pid = p.uid
            # scene updates
            scene_update(scene)
        except Exception as my_err:
            print(f"sub_parent: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


class PTDOBRELS_OT_sub(bpy.types.Operator):
    bl_label = "Edit Sub"
    bl_idname = "ptdobrels.sub"
    bl_description = "edit sub system"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    pid: bpy.props.StringProperty(default="")
    iloc: bpy.props.FloatVectorProperty(
        size=3, default=[0, 0, 0], subtype="TRANSLATION"
    )
    rotang: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0], subtype="EULER")
    rotpiv: bpy.props.EnumProperty(
        name="Pivot",
        description="rotation pivot",
        items=(("object", "object", "object"), ("parent", "parent", "parent")),
        default="parent",
    )
    rotinf: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        props = context.scene.ptdobrels_props
        return bool(props.subs)

    def invoke(self, context, event):
        props = context.scene.ptdobrels_props
        item = props.subs[props.subs_idx]
        pd = self.as_keywords()
        for key in pd.keys():
            setattr(self, key, getattr(item, key))
        if not self.pid:
            self.rotinf = False
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        item = props.subs[props.subs_idx]
        pd = self.as_keywords(ignore=("pid",))
        for key in pd.keys():
            setattr(item, key, getattr(self, key))
        try:
            scene_update(scene)
        except Exception as my_err:
            print(f"sub_edit: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ["Location", "Rot. Angle", "Rot. Pivot", "Rot. Influence"]
        for name in names:
            row = sc.row()
            row.label(text=name)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "iloc", text="")
        row = sc.row(align=True)
        row.prop(self, "rotang", text="")
        row = sc.row(align=True)
        row.prop(self, "rotpiv", text="")
        row = sc.row(align=True)
        row.enabled = bool(self.pid)
        row.prop(self, "rotinf", text="Inherit Parent Rotation", toggle=True)


class PTDOBRELS_OT_obnames(bpy.types.Operator):
    bl_label = "Show Names"
    bl_idname = "ptdobrels.obnames"
    bl_description = "toggle object name visibility in viewport"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        try:
            for item in props.subs:
                if item.pnt_ob:
                    item.pnt_ob.show_name = not item.pnt_ob.show_name
        except Exception as my_err:
            print(f"obnames: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


# ------------------------------------------------------------------------------
#
# ---------------------------- USER INTERFACE ----------------------------------

# ---- USER LISTS


class PTDOBRELS_UL_subs(bpy.types.UIList):
    """sub list"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        p_name = ""
        if item.pid:
            for i in data.subs:
                if i.uid == item.pid:
                    p_name = i.name
                    break
        col = layout.column()
        col.prop(item, "name", text="", emboss=False, icon="RADIOBUT_ON")
        col = layout.column()
        col.label(text=f"p: {p_name}")


# ---- PANELS


class PTDOBRELS_PT_ui(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "RELS"
    bl_label = "Object Relations"

    @classmethod
    def poll(cls, context):
        return req_check(context.scene)

    def draw(self, context):
        scene = context.scene
        props = scene.ptdobrels_props
        layout = self.layout

        layout.enabled = not context.screen.is_animation_playing

        c = layout.column(align=True)
        row = c.row(align=True)
        row.operator("ptdobrels.sub_add")
        row.operator("ptdobrels.sub_remove").doall = False
        row.operator("ptdobrels.sub_remove", text="Clear").doall = True
        row = c.row(align=True)

        subs = props.subs
        subsid = props.subs_idx

        row.enabled = bool(subs)
        row.template_list(
            "PTDOBRELS_UL_subs", "", props, "subs", props, "subs_idx", rows=2, maxrows=4
        )
        row = c.row(align=True)
        row.enabled = bool(subs)
        row.operator("ptdobrels.sub", text="Edit")
        row = c.row(align=True)
        row.enabled = bool(subs)
        col = row.column(align=True)
        row = col.row(align=True)
        if bool(subs):
            item = subs[subsid]
            row = col.row(align=True)
            row.prop(item, "object_color", text="")
            row.prop(item, "object_scale", text="")
            row = col.row(align=True)
            row.operator("ptdobrels.obnames", text="Toggle Object Names")
            row = col.row(align=True)
            # parent links
            box = col.box()
            p_links = props.p_idx > -1
            box.enabled = p_links
            row = box.row(align=True)
            pflag = p_links and (subs[props.p_idx].uid != item.pid)
            cap = "Set Parent" if pflag else "Free Parent"
            row.operator("ptdobrels.sub_parent", text=cap).val = pflag
            row.prop(props, "parent_enum", text="")
        else:
            row.label(text="no subs")


# ------------------------------------------------------------------------------
#
# ---------------------------- REGISTER OBJECTS --------------------------------

classes = (
    PTDOBRELS_sub,
    PTDOBRELS_props,
    PTDOBRELS_OT_sub_add,
    PTDOBRELS_OT_sub_remove,
    PTDOBRELS_OT_sub_parent,
    PTDOBRELS_OT_sub,
    PTDOBRELS_OT_obnames,
    PTDOBRELS_UL_subs,
    PTDOBRELS_PT_ui,
)


def fcpre(scene):
    val = radians((scene.frame_current - 1) * 3)
    scene_update_frames(scene, val)


def remove_fcpre_handlers():
    fcpre_handlers = [
        h for h in bpy.app.handlers.frame_change_pre if h.__name__ == "fcpre"
    ]
    for h in fcpre_handlers:
        bpy.app.handlers.frame_change_pre.remove(h)


def register():
    remove_fcpre_handlers()

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.ptdobrels_props = bpy.props.PointerProperty(type=PTDOBRELS_props)

    bpy.app.handlers.frame_change_pre.append(fcpre)


def unregister():
    remove_fcpre_handlers()

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ptdobrels_props


# ------------------------------------------------------------------------------
#
# ------------------------------ RUN MODULE ------------------------------------

if __name__ == "__main__":
    print("-" * 30)
    register()
    unregister()
