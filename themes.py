from effects import *


THEMES = {
    "default": {
        "font": "RubikWetPaint-Regular.ttf",
        "fontsize": 0.03,
        "width_part": 0.9,
        "x_spacing": 0.1,
        "stroke": True,
        "stroke_part": 0.2,
        "rotation_degrees": 0,
        "effect": [fade_effect, words_lead_effect],
        "effect_params": [
            {"fadein": 0.25, "fadeout": 0.25},
            {"karaoke": True}
        ]
    },
    "HORMOZI 1": {
        "font": "Montserrat-VariableFont_wght.ttf",
        "fontsize": 0.03,
        "x_spacing": 0.3,
        "uppercase": True,
        "width_part": 0.9,
        "font_variation": "ExtraBold",
        "stroke": True,
        "stroke_part": 0.17,
        "effect": [rotation_effect, increase_effect],
        "effect_params": [
            {"maximum_rotation": 25},
            {"start_font": 0.95, "end_font": 1.1}
        ]
    }
}
