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


class BoneNamingPreset(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Preset Name")
    prefixes: bpy.props.CollectionProperty(type=BoneNamingPrefix)
    middle_words: bpy.props.CollectionProperty(type=BoneNamingMiddleWord)
    suffixes: bpy.props.CollectionProperty(type=BoneNamingSuffix)
    counter_settings: bpy.props.PointerProperty(type=BoneCounterSettings)
    side_pair_settings: bpy.props.PointerProperty(type=BoneSidePairSettings)
    separator_settings: bpy.props.PointerProperty(type=BoneSeparatorSettings)

    def generate_regex_cache(self):
        pass

    def validate_data(self):
        pass


class BoneNamingPresets(bpy.types.PropertyGroup):
    is_cache_valid = False

    presets: bpy.props.CollectionProperty(type=BoneNamingPreset)
    active_preset_index: bpy.props.IntProperty(name="Active Preset Index")

    def on_preset_selected(self):
        pass

    def create_pie_menu_items(self, context):
        pass

    def export_presets(self, file_path):
        pass

    def import_presets(self, file_path):
        pass

    def on_edit(self, context):
        self.is_cache_valid = False

if __name__ == "__main__":
    pass
