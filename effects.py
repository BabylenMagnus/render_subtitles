import numpy as np
from PIL import ImageFont

from core import TextSubtitle


def fade_effect(
        start: int, end: int, fps: int, fadein: float, fadeout: float, start_point: float = 0.2
):
    fadein = min(int(fps * fadein) + 1, (end-start) // 2)
    fadeout = min(int(fps * fadeout) + 1, (end-start) // 2)

    fadein_list = np.linspace(start_point, 1, fadein)
    fadeout_list = np.linspace(start_point, 1, fadeout)[::-1]

    def effect(i, subtitle: TextSubtitle):
        if start <= i < start + fadein:
            subtitle.color[-1] = int(fadein_list[i - start] * 255)
        if end - fadeout <= i < end:
            subtitle.color[-1] = int(fadeout_list[i - (end - fadeout)] * 255)

        i += 1
        return subtitle

    return effect


def bouncing_effect(
        start: int, end: int, fps: int, bounce_up: float = 0.4, bounce_normal: float = 0.4,
        minimum_font: float = 0.8, maximum_font: float = 1.4, end_font: float = 1.2
):
    bounce_up = min(int(fps * bounce_up) + 1, (end-start) // 2)
    bounce_normal = min(int(fps * bounce_normal) + 1, (end-start) // 2)

    bounce_up_list = np.linspace(minimum_font, maximum_font, bounce_up)
    bounce_normal_list = np.linspace(maximum_font, end_font, bounce_normal)

    def effect(i, subtitle: TextSubtitle):
        if start <= i < start + bounce_up:
            subtitle.font = ImageFont.truetype(
                subtitle.font_path,
                subtitle.font_size * bounce_up_list[i - start]
            )
        if end - bounce_normal <= i < end:
            subtitle.font = ImageFont.truetype(
                subtitle.font_path,
                subtitle.font_size * bounce_normal_list[i - (end - bounce_normal)]
            )

        i += 1
        return subtitle

    return effect
