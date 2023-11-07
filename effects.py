import numpy as np

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
