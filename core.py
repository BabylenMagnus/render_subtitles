from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

from config import FONT_PATH, SPLIT_CHAR


class TextSubtitle:
    font: None

    def __init__(
            self, text: str, words: list[dict], width: int, height: int, x_spacing: float,
            width_part: float, font: str, fontsize: float, color: list = [0, 0, 0, 255],
            second_color: list = [0, 128, 0, 255], h_space: int = 0.005
    ):
        self.text = text
        self.words = words
        self.width_text = int(width * width_part)

        self.width = width
        self.height = height

        self.x_spacing = height - int(x_spacing * height)

        self.font_path = os.path.join(FONT_PATH, font)
        self.font_size = int(height * fontsize)
        self.h_space = int(height * h_space)

        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.color = color if len(color) == 4 else color + [255]
        self.second_color = second_color if len(second_color) == 4 else second_color + [255]

        self.pieces = None
        self.y_start = None

        self.calculate_pieces()

    def break_fix(self, text, draw):
        """
        Fix line breaks in text.
        """
        if not text:
            return
        if isinstance(text, str):
            text = text.split()  # this creates a list of words
        lo = 0
        hi = len(text)
        if hi == 1:
            left, top, right, bottom = draw.textbbox((0, 0), text[0], font=self.font)
            yield text[0], right - left, bottom - top
        else:
            while lo < hi:
                mid = (lo + hi + 1) // 2
                temp_text = ' '.join(text[:mid])  # this makes a string again
                left, top, right, bottom = draw.textbbox((0, 0), temp_text, font=self.font)

                if right - left <= self.width_text:
                    lo = mid
                else:
                    hi = mid - 1

                if right - left <= self.width_text and len(temp_text.split(" ")) == 1:
                    break

            temp_text = ' '.join(text[:lo])  # this makes a string again
            left, top, right, bottom = draw.textbbox((0, 0), temp_text, font=self.font)

            yield temp_text, right - left, bottom - top
            yield from self.break_fix(text[lo:], draw)

    def calculate_pieces(self):
        txt_layer = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        self.pieces = list(self.break_fix(self.text, draw))
        self.pieces = [list(i) for i in self.pieces]
        self.y_start = self.x_spacing - sum(p[2] for p in self.pieces)

    def fit_text(self, img):
        """
        Fit text into container after applying line breaks. Returns the total
        height taken up by the text, which can be used to create containers of
        dynamic heights.
        """
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        y = self.y_start

        for temp_text, w, h in self.pieces:

            left, top, right, bottom = draw.textbbox((0, 0), temp_text.replace(SPLIT_CHAR, ""), font=self.font)
            x = (img.size[0] - (right - left)) // 2
            w_start = x

            for i, t in enumerate(temp_text.split(SPLIT_CHAR)):
                draw.text((w_start, y), t, font=self.font, fill=tuple([self.color, self.second_color][i % 2]))
                left, top, right, bottom = draw.textbbox((0, 0), t, font=self.font)
                w_start += right - left

            y += h + self.h_space

        img = Image.alpha_composite(img, txt_layer)

        return img

    def __call__(self, frame):
        frame = Image.fromarray(frame)
        frame = frame.convert("RGBA")
        frame = self.fit_text(frame)
        frame = frame.convert("RGB")
        return np.array(frame)


class FragmentSubtitle:
    def __init__(
            self, start_time, end_time, width: int, height: int, fps: float,
            text: str, words: list[dict], subtitle_settings: dict, effect=None, effect_params: dict = None
    ):
        self.start = int(start_time * fps)
        self.end = int(end_time * fps)

        self.subtitle = TextSubtitle(text, words, width, height, **subtitle_settings)

        self.effects = []
        if isinstance(effect, list):
            for ef, params in zip(effect, effect_params):
                self.effects.append(ef(self.start, self.end, fps, **params))
        elif effect is None:
            self.effects = None
        else:
            self.effects.append(effect(self.start, self.end, fps, **effect_params))

    def __call__(self, i: int, frame: np.array):
        if self.start <= i <= self.end:
            if self.effects is not None:
                for effect in self.effects:
                    self.subtitle = effect(i, self.subtitle)
            return self.subtitle(frame)
        return frame


class SubtitleStream:
    def __init__(
            self, segments: list[dict], width: int, height: int, fps: float,
            subtitle_settings: dict, effect=None, effect_params: dict = None
    ):
        self.segments = [
            FragmentSubtitle(
                seg["start"], seg["end"], width, height, fps, seg["text"], seg["words"],
                subtitle_settings, effect, effect_params
            )
            for seg in segments
        ]
        self.index = 0
        self.current_sub = self.segments[0]
        self.segments.remove(self.current_sub)

    def __call__(self, frame: np.array):
        if self.current_sub is None:
            return frame

        self.index += 1
        frame = self.current_sub(self.index, frame)

        if self.current_sub.end < self.index:

            self.current_sub = self.segments[0] if len(self.segments) else None
            if self.current_sub is not None:
                self.segments.remove(self.current_sub)

        return frame
