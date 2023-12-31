from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

from config import FONT_PATH, SPLIT_CHAR


class TextSubtitle:
    font: None

    def __init__(
            self, text: str, words: list[dict], width: int, height: int, y_spacing: float, width_part: float,
            font: str, fontsize: float, color: list = [255, 255, 255, 255], second_color: list = [0, 128, 0, 255],
            stroke_color: list = [0, 0, 0, 255], stroke: bool = False, stroke_part: float = 1.4, h_space: int = 0.005,
            rotation_degrees: float = 0.0, uppercase: bool = False, font_variation: str = None, scale_value: float = 1.0
    ):
        self.text = text.upper() if uppercase else text
        self.words = words
        if uppercase:
            for word in words:
                word["word"] = word["word"].upper()
        self.width_text = int(width * width_part)

        self.stroke = stroke
        self.stroke_part = stroke_part

        self.width = width
        self.height = height

        self.y_spacing = height - int(y_spacing * height)

        self.font_path = os.path.join(FONT_PATH, font)
        self.font_size = int(height * fontsize)
        self.h_space = int(height * h_space)

        self.font = None
        self.font_variation = font_variation
        self.set_font()

        self.color = color if len(color) == 4 else color + [255]
        self.second_color = second_color if len(second_color) == 4 else second_color + [255]
        self.stroke_color = stroke_color if len(stroke_color) == 4 else stroke_color + [255]

        self.pieces = None
        self.y_start = None
        self.text_height = None

        self.rotation_degrees = rotation_degrees
        self.scale_value = scale_value
        self.calculate_pieces()

    def set_font(self, font_path=None, font_size=None, font_variation=None):
        font_path = self.font_path if font_path is None else font_path
        font_size = self.font_size if font_size is None else font_size
        font_variation = self.font_variation if font_variation is None else font_variation

        self.font = ImageFont.truetype(font_path, font_size)
        if not font_variation is None:
            self.font.set_variation_by_name(font_variation)

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
                left, top, right, bottom = draw.textbbox(
                    (0, 0), temp_text, font=self.font,
                    stroke_width=int(self.font_size * self.stroke_part * int(self.stroke))
                )

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
        self.text_height = sum(p[2] for p in self.pieces)
        self.y_start = self.y_spacing - self.text_height

    def fit_text(self, img):
        """
        Fit text into container after applying line breaks. Returns the total
        height taken up by the text, which can be used to create containers of
        dynamic heights.
        """
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))

        rotated_img = Image.new(
            'RGBA',
            (
                int(max(x[1] for x in self.pieces) * 1.2),
                int((self.text_height + self.text_height * self.stroke_part) * 1.5)
            ),
            (255, 255, 255, 0)
        )
        rotated_draw = ImageDraw.Draw(rotated_img)
        y = 0

        for temp_text, w, h in self.pieces:

            left, top, right, bottom = rotated_draw.textbbox(
                (0, 0), temp_text.replace(SPLIT_CHAR, ""), font=self.font,
                stroke_width=int(self.font_size * self.stroke_part * int(self.stroke))
            )
            x = (rotated_img.size[0] - (right - left)) // 2
            w_start = x

            for i, t in enumerate(temp_text.split(SPLIT_CHAR)):
                left, top, right, bottom = rotated_draw.textbbox((0, 0), t, font=self.font)

                rotated_draw.text(
                    (w_start, y), t, font=self.font, fill=tuple([self.color, self.second_color][i % 2]),
                    stroke_fill=tuple(self.stroke_color),
                    stroke_width=int(self.font_size * self.stroke_part * int(self.stroke))
                )
                w_start += right - left

            y += h + self.h_space

        if self.rotation_degrees != 1.0:
            rotated_img = rotated_img.rotate(self.rotation_degrees, expand=1)
        if self.scale_value != 1.0:
            rotated_img = rotated_img.resize(
                (int(rotated_img.size[0] * self.scale_value), int(rotated_img.size[1] * self.scale_value))
            )

        txt_layer.paste(
            rotated_img,
            ((txt_layer.size[0] - rotated_img.size[0]) // 2, self.y_spacing - rotated_img.size[1] // 2),
            rotated_img
        )

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
            text: str, words: list[dict], subtitle_settings: dict
    ):
        self.start = int(start_time * fps)
        self.end = int(end_time * fps)

        effect = subtitle_settings.pop("effect", None)
        effect_params = subtitle_settings.pop("effect_params", [])

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
            subtitle_settings: dict
    ):
        color = subtitle_settings.pop("color", [255, 255, 255, 255])
        second_color = subtitle_settings.pop("second_color", [0, 128, 0, 255])

        self.segments = []

        for i, seg in enumerate(segments):
            subtitle_settings["color"] = color[i % len(color)] if isinstance(color[0], list) else color
            subtitle_settings["second_color"] = second_color[i % len(second_color)] \
                if isinstance(second_color[0], list) else second_color

            self.segments.append(
                FragmentSubtitle(
                    seg["start"], seg["end"], width, height, fps, seg["text"], seg["words"],
                    subtitle_settings.copy()
                )
            )

        self.index = 0
        self.current_sub = self.segments[0]
        self.segments.remove(self.current_sub)

    def get_sub(self, index: int):
        for current_sub in self.segments:
            if current_sub.start <= index <= current_sub.end:
                return current_sub
