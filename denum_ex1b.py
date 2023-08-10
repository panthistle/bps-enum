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


# Example 1b: coordinate two enum properties with mutually exclusive values
#             [using get/set callbacks]


import bpy


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class DENUMS2_props(bpy.types.PropertyGroup):
    def track_get(self):
        # note: the default value for enum-property must be a numeric index
        return self.get("track", 1)

    def track_set(self, value):
        # note: the 'value' parameter also holds a numeric index
        u = self.get("up", 2)
        if value in [u, u + 3]:
            # adjust selected index so it does not clash with UP property
            value = value + 1 if value < 5 else 0
        self["track"] = value

    def up_get(self):
        return self.get("up", 2)

    def up_set(self, value):
        t = self.get("track", 1)
        if t in [value, value + 3]:
            # adjust selected index so it does not clash with TRACK property
            value = value + 1 if value < 2 else 0
        self["up"] = value

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
        get=track_get,
        set=track_set,
    )

    up: bpy.props.EnumProperty(
        name="Up",
        description="up axis",
        items=(("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z")),
        default="Z",
        get=up_get,
        set=up_set,
    )


# ------------------------------------------------------------------------------
#
# --------------------------------- PANEL --------------------------------------


class DENUMS2_PT_ui(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "DENUMS2"
    bl_label = "DENUMS2"

    def draw(self, context):
        props = context.scene.denum_t2
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
    DENUMS2_props,
    DENUMS2_PT_ui,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.denum_t2 = bpy.props.PointerProperty(type=DENUMS2_props)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.denum_t2


# ------------------------------------------------------------------------------
#
# ------------------------------- RUN MODULE -----------------------------------

if __name__ == "__main__":
    print("-" * 30)
    register()
    unregister()
