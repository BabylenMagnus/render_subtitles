import random
import numpy as np

from core import TextSubtitle
from config import SPLIT_CHAR


__all__ = ['fade_effect', 'bouncing_effect', 'words_lead_effect', 'rotation_effect', 'increase_effect']


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
            subtitle.second_color[-1] = int(fadein_list[i - start] * 255)
            subtitle.stroke_color[-1] = int(fadein_list[i - start] * 255)
        if end - fadeout <= i < end:
            subtitle.color[-1] = int(fadeout_list[i - (end - fadeout)] * 255)
            subtitle.second_color[-1] = int(fadeout_list[i - (end - fadeout)] * 255)
            subtitle.stroke_color[-1] = int(fadeout_list[i - (end - fadeout)] * 255)

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
            subtitle.scale_value = bounce_up_list[i - start]
        if end - bounce_normal <= i < end:
            subtitle.scale_value = bounce_normal_list[i - (end - bounce_normal)]
        return subtitle

    return effect


def words_lead_effect(
        start: int, end: int, fps: int, karaoke: bool = False
):
    def effect(i, subtitle: TextSubtitle):
        out_text = []
        w = [word["word"].strip() for word in subtitle.words]

        for piece_ in subtitle.pieces:
            piece_ = piece_[0].replace(SPLIT_CHAR, "").split()
            start_i, end_i = w.index(piece_[0]), w.index(piece_[-1]) + 1
            out_text.append("")

            for word in subtitle.words[start_i: end_i]:
                if word["start"] * fps <= i:
                    if i <= word["end"] * fps or karaoke:
                        out_text[-1] += SPLIT_CHAR + word["word"] + SPLIT_CHAR
                else:
                    out_text[-1] += word["word"]

        for i in range(len(subtitle.pieces)):
            subtitle.pieces[i][0] = out_text[i]
        return subtitle

    return effect


def rotation_effect(
        start: int, end: int, fps: int, maximum_rotation: float = 25.0
):
    possible_rotation = [i for i in range(1, maximum_rotation)] + [360 - i for i in range(1, maximum_rotation)]
    degree = random.choice(possible_rotation)

    def effect(i, subtitle: TextSubtitle):
        subtitle.rotation_degrees = degree
        return subtitle

    return effect


def increase_effect(
        start: int, end: int, fps: int, start_font: float = 0.8, end_font: float = 1.2
):
    increase_list = np.linspace(start_font, end_font, end - start + 1)

    def effect(i, subtitle: TextSubtitle):
        subtitle.scale_value = increase_list[i - start]
        return subtitle

    return effect
