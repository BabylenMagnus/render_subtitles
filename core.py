from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

from config import FONT_PATH


class TextSubtitle:
    font: None

    def __init__(
            self, text: str, width: int, height: int, x_spacing: float, width_part: float,
            font: str, fontsize: float, color: list = [0, 0, 0, 255]
    ):
        self.text = text
        self.width = int(width * width_part)
        self.x_spacing = height - int(x_spacing * height)

        self.font = ImageFont.truetype(os.path.join(FONT_PATH, font), int(height * fontsize))
        self.color = color if len(color) == 4 else color + [255]

    def break_fix(self, text, font, draw):
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
            left, top, right, bottom = draw.textbbox((0, 0), text[0], font=font)
            yield text[0], right - left, bottom - top
        else:
            while lo < hi:
                mid = (lo + hi + 1) // 2
                temp_text = ' '.join(text[:mid])  # this makes a string again
                left, top, right, bottom = draw.textbbox((0, 0), temp_text, font=font)

                if right - left <= self.width:
                    lo = mid
                else:
                    hi = mid - 1

                if right - left <= self.width and len(temp_text.split(" ")) == 1:
                    break

            temp_text = ' '.join(text[:lo])  # this makes a string again
            left, top, right, bottom = draw.textbbox((0, 0), temp_text, font=font)

            yield temp_text, right - left, bottom - top
            yield from self.break_fix(text[lo:], font, draw)

    def fit_text(self, img):
        """
        Fit text into container after applying line breaks. Returns the total
        height taken up by the text, which can be used to create containers of
        dynamic heights.
        """
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        pieces = list(self.break_fix(self.text, self.font, draw))
        height = sum(p[2] for p in pieces)
        y = self.x_spacing - height

        h_taken_by_text = 0
        for t, w, h in pieces:
            x = (img.size[0] - w) // 2
            draw.text((x, y), t, font=self.font, fill=tuple(self.color))
            left, top, right, bottom = draw.textbbox((0, 0), t, font=self.font)
            y += h
            h_taken_by_text += bottom - top

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
            text: str, subtitle_settings: dict, effect=None, effect_params: dict = None
    ):
        self.start = int(start_time * fps)
        self.end = int(end_time * fps)

        self.subtitle = TextSubtitle(text, width, height, **subtitle_settings)

        self.effect = None if effect is None else effect(self.start, self.end, fps, **effect_params)

    def __call__(self, i: int, frame: np.array):
        if self.start <= i <= self.end:
            if self.effect is not None:
                self.subtitle = self.effect(i, self.subtitle)
            return self.subtitle(frame)
        return frame


class SubtitleStream:
    def __init__(
            self, segments: list[dict], width: int, height: int, fps: float,
            subtitle_settings: dict, effect=None, effect_params: dict = None
    ):
        self.segments = [
            FragmentSubtitle(
                seg["start"], seg["end"], width, height, fps, seg["text"],
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
