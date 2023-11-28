import bpy


class BoneNamingPrefix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")

class BoneNamingMiddleWord(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")

class BoneNamingSuffix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")

class BoneCounterSettings(bpy.types.PropertyGroup):
    digits: bpy.props.IntProperty(name="Digits", default=2, min=1, max=5)

class BoneSidePairSettings(bpy.types.PropertyGroup):
    side_pair: bpy.props.EnumProperty(
        name="Side Pair",
        description="Left/Right side pair format",
        items=[
            ('LR', "L / R", "Upper case L/R", 1),
            ('lr', "l / r", "Lower case l/r", 2),
            ('LEFT_RIGHT', "LEFT / RIGHT", "Full word LEFT/RIGHT", 3),
            ('left_right', "left / right", "Full word left/right", 4),
        ],
        default='LR'
    )
    separator: bpy.props.EnumProperty(
        name="Separator",
        description="Separator for left/right",
        items=[
            ('_', "Underscore", "_"),
            ('.', "Dot", "."),
            ('-', "Dash", "-"),
            (' ', "Space", " "),
            ('', "None", ""),
        ],
        default='_'
    )
    position: bpy.props.EnumProperty(
        name="Position",
        description="Position of side pair",
        items=[
            ('PREFIX', "Prefix", "Before the name"),
            ('SUFFIX', "Suffix", "After the name"),
        ],
        default='SUFFIX'
    )

class BoneSeparatorSettings(bpy.types.PropertyGroup):
    separator: bpy.props.EnumProperty(
        name="Separator",
        items=[
            ('_', "Underscore", "_"),
            ('.', "Dot", "."),
            ('-', "Dash", "-"),
            (' ', "Space", " "),
        ],
        default='_'
    )


if __name__ == "__main__":
    pass
