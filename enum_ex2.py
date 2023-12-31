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


# Example 2: control the number of custom-list-items to display


import bpy


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class DENUMCTRL_props(bpy.types.PropertyGroup):
    def optenum_items(self, context):
        # this function will populate 'optenum' with a number of items
        # from the 'names' list, specified by the 'ctrl' property
        names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        items = []
        for i in range(self.ctrl):
            items.append((names[i], names[i], names[i]))
        return items

    def ctrl_update(self, context):
        # note: you MUST select index here, otherwise it will be undefined
        # In this case, we set it to the last item in the list
        names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
        items = self.get("ctrl", 3)
        self.optenum = names[items - 1]

    # enumerated list
    optenum: bpy.props.EnumProperty(
        name="Options",
        description="selection list",
        items=optenum_items,
    )
    # controls the number of items for enumerated list
    ctrl: bpy.props.IntProperty(default=3, min=3, max=12, update=ctrl_update)


# ------------------------------------------------------------------------------
#
# --------------------------------- PANEL --------------------------------------


class DENUMCTRL_PT_ui(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "DENUMCTRL"
    bl_label = "DENUMCTRL"

    def draw(self, context):
        props = context.scene.denum_opt
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Items:")
        row.prop(props, "ctrl", text="")
        row = box.row(align=True)
        row.prop(props, "optenum", text="")
        row = box.row(align=True)
        row.label(text="Current Index")
        row.label(text=f'{props.get("optenum", 0)}')


# ------------------------------------------------------------------------------
#
# ------------------------------ REGISTRATION ----------------------------------

classes = (
    DENUMCTRL_props,
    DENUMCTRL_PT_ui,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.denum_opt = bpy.props.PointerProperty(type=DENUMCTRL_props)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.denum_opt


# ------------------------------------------------------------------------------
#
# ------------------------------- RUN MODULE -----------------------------------

if __name__ == "__main__":
    print("-" * 30)
    register()
    unregister()
