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


# Example 1: coordinate two enum properties with mutually exclusive values


import bpy


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class DENUMSYNC_props(bpy.types.PropertyGroup):
    def up_items(self, context):
        # this function will populate 'up' enum with valid entries
        # that do not clash with currently selected 'track' value 
        names = ["X", "Y", "Z"]
        t = self.get("track", 1)
        items = []
        for i in range(3):
            if t in [i, i + 3]:
                continue
            items.append((names[i], names[i], names[i]))
        return items

    track: bpy.props.EnumProperty(
        name="Track",
        description="track axis",
        items=(
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
            ("-X", "-X", "-X"),
            ("-Y", "-Y", "-Y"),
            ("-Z", "-Z", "-Z"),
        ),
        default="Y",
    )

    up: bpy.props.EnumProperty(
        name="Up",
        description="up axis",
        items=up_items,
    )


# ------------------------------------------------------------------------------
#
# --------------------------------- PANEL --------------------------------------


class DENUMSYNC_PT_ui(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "DENUMSYNC"
    bl_label = "DENUMSYNC"

    def draw(self, context):
        props = context.scene.denum_tu
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Track")
        row.label(text="Up")
        row = col.row(align=True)
        row.prop(props, "track", text="")
        row.prop(props, "up", text="")


# ------------------------------------------------------------------------------
#
# ------------------------------ REGISTRATION ----------------------------------

classes = (
    DENUMSYNC_props,
    DENUMSYNC_PT_ui,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.denum_tu = bpy.props.PointerProperty(type=DENUMSYNC_props)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.denum_tu


# ------------------------------------------------------------------------------
#
# ------------------------------- RUN MODULE -----------------------------------

if __name__ == "__main__":
    print("-" * 30)
    register()
    unregister()
