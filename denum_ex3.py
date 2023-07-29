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


# Example 3: Sync enum property with user-list. The requirement is that for any
#            selected item in the user-list, the "enum" should contain valid
#            parent candidates. This means it will not show any of the selected
#            item's descendants (children, grand-children, and so on).


import bpy
import uuid


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class DENUMUL_sub(bpy.types.PropertyGroup):
    # user-list item properties

    name: bpy.props.StringProperty(default="sub")
    # item/parent unique ids
    uid: bpy.props.StringProperty(default="")
    pid: bpy.props.StringProperty(default="")


class DENUMUL_props(bpy.types.PropertyGroup):
    def descendants(self, key, lst=[]):
        # for any item with uid==key, return a list of uids of dependent items
        # - first, we get the item's children
        cuids = [sub.uid for sub in self.subs if sub.pid == key]
        for cuid in cuids:
            # - then, for each child, we append its uid to the list
            lst.append(cuid)
            # - and call the function recursively to traverse the tree of descendants
            lst = self.descendants(cuid, lst)
        return lst

    def parent_enum_items(self, context):
        # calls to this function will update the 'parent_enum' list
        items = []
        if not bool(self.subs):
            return items
        idx = self.subs_idx
        key = self.subs[idx].uid
        # populate 'parent_enum' list with valid parent candidates
        # exclude current item and its descendants
        duids = self.descendants(key, [])
        for i, item in enumerate(self.subs):
            if (i == idx) or (item.uid in duids):
                continue
            items.append((str(i), item.name, "", i))
        return items

    def parent_enum_update(self, context):
        # update parent_enum index
        self.p_idx = self.get("parent_enum", -1)

    def subs_idx_update(self, context):
        # update parent_enum index
        self.p_idx = -1
        if bool(self.subs):
            # get the current 'parent_enum' items list
            items = self.parent_enum_items(context)
            if bool(items):
                # this triggers 'parent_enum_update'
                self.parent_enum = items[0][0]

    # parent_enum index
    p_idx: bpy.props.IntProperty(default=-1)
    # parent_enum list
    parent_enum: bpy.props.EnumProperty(
        name="Parent Links",
        description="target parent",
        items=parent_enum_items,
        update=parent_enum_update,
        options={"HIDDEN"},
    )
    # user-list collection
    subs: bpy.props.CollectionProperty(type=DENUMUL_sub)
    # user-list index
    subs_idx: bpy.props.IntProperty(
        name="sub", default=-1, update=subs_idx_update, options={"HIDDEN"}
    )


# ------------------------------------------------------------------------------
#
# ------------------------------ OPERATORS -------------------------------------


class DENUMUL_OT_sub_add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "denumul.sub_add"
    bl_description = "add item"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = scene.denumul_props
        try:
            item = props.subs.add()
            item.uid = self.sub_uid_get()
            props.subs_idx = len(props.subs) - 1
        except Exception as my_err:
            self.report({"INFO"}, f"{my_err.args}")
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


class DENUMUL_OT_sub_remove(bpy.types.Operator):
    bl_label = "Remove"
    bl_idname = "denumul.sub_remove"
    bl_description = "remove item"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    # delete item(s) flag: True=All, False=Current
    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = context.scene.denumul_props
        return bool(props.subs)

    def execute(self, context):
        scene = context.scene
        props = scene.denumul_props
        try:
            if self.doall:
                props.subs.clear()
                props.subs_idx = -1
                props.p_idx = -1
                return {"FINISHED"}
            idx = props.subs_idx
            obj = props.subs[idx]
            # update parent-reference of any children before removing
            for item in props.subs:
                if item.pid == obj.uid:
                    item.pid = obj.pid
            props.subs.remove(idx)
            props.subs_idx = min(max(0, idx - 1), len(props.subs) - 1)
            # update ui-panel display flag if there are no items left
            if props.subs_idx < 0:
                props.p_idx = -1
        except Exception as my_err:
            self.report({"INFO"}, f"{my_err.args}")
            print(f"sub_remove: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


class DENUMUL_OT_sub_parent(bpy.types.Operator):
    bl_label = "Set Parent"
    bl_idname = "denumul.sub_parent"
    bl_description = "set item parent"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    # parent flag: True=assign, False=release
    val: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        props = scene.denumul_props
        try:
            obj = props.subs[props.subs_idx]
            if not self.val:
                obj.pid = ""
            else:
                parent = props.subs[int(props.parent_enum)]
                obj.pid = parent.uid
        except Exception as my_err:
            self.report({"INFO"}, f"{my_err.args}")
            print(f"sub_parent: {my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


# ------------------------------------------------------------------------------
#
# ---------------------------- USER INTERFACE ----------------------------------

# ---- USER LIST


class DENUMUL_UL_subs(bpy.types.UIList):
    """user list"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        p_name = ""
        if item.pid:
            for obj in data.subs:
                if obj.uid == item.pid:
                    p_name = obj.name
                    break
        col = layout.column()
        col.prop(item, "name", text="", emboss=False, icon="RADIOBUT_ON")
        col = layout.column()
        col.label(text=f"p: {p_name}")


# ---- PANEL


class DENUMUL_PT_ui(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "DENUMUL"
    bl_label = "DENUMUL"

    def draw(self, context):
        scene = context.scene
        props = scene.denumul_props
        layout = self.layout
        c = layout.column(align=True)
        row = c.row(align=True)
        row.operator("denumul.sub_add")
        row.operator("denumul.sub_remove", text="Remove").doall = False
        row.operator("denumul.sub_remove", text="Clear").doall = True
        row = c.row(align=True)

        subs = props.subs
        subid = props.subs_idx

        row.enabled = bool(subs)
        row.template_list(
            "DENUMUL_UL_subs", "", props, "subs", props, "subs_idx", rows=2, maxrows=4
        )
        row = c.row(align=True)
        row.enabled = bool(subs)
        col = row.column(align=True)
        row = col.row(align=True)
        if bool(subs):
            item = subs[subid]
            box = col.box()
            box.label(text="Parent Links")
            box.enabled = len(subs) > 1
            col = box.column(align=True)
            row = col.row(align=True)
            rc = row.column(align=True)
            p_idx = props.p_idx
            # enable the parent operator if parent_enum is populated
            rc.enabled = (p_idx > -1)
            # if the current selection is NOT the parent of 'item'
            # call [assign-parent], otherwise call [remove-parent]
            pflag = (subs[p_idx].uid != item.pid)
            cap = "Assign Parent" if pflag else "Remove Parent"
            rc.operator("denumul.sub_parent", text=cap).val = pflag
            rc = row.column(align=True)
            rc.prop(props, "parent_enum", text="")
        else:
            row.label(text="no items")


# ------------------------------------------------------------------------------
#
# ------------------------------ REGISTRATION ----------------------------------

classes = (
    DENUMUL_sub,
    DENUMUL_props,
    DENUMUL_OT_sub_add,
    DENUMUL_OT_sub_remove,
    DENUMUL_OT_sub_parent,
    DENUMUL_UL_subs,
    DENUMUL_PT_ui,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.denumul_props = bpy.props.PointerProperty(type=DENUMUL_props)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.denumul_props


# ------------------------------------------------------------------------------
#
# ------------------------------- RUN MODULE -----------------------------------

if __name__ == "__main__":
    print("-" * 30)
    register()
    unregister()
