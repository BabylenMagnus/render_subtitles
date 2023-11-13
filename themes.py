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
        "fontsize": 0.04,
        "x_spacing": 0.45,
        "uppercase": True,
        "width_part": 0.9,
        "font_variation": "ExtraBold"
    }
}
