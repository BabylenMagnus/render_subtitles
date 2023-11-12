from core import SubtitleStream

import cv2


def fix_words(segments: list[dict]):
    new_segments = []
    for seg in segments:
        words = seg["words"]
        k = 0
        for i in range(len(words)):
            if words[i - k]["word"].startswith("-"):
                words[i - k - 1]["word"] += words[i - k]["word"]
                words[i - k - 1]["end"] = words[i - k]["end"]
                del words[i - k]
                k += 1
        seg["words"] = words
        new_segments.append(seg)

    return segments


def render_subtitles(
        segments: list[dict], video_input_path: str,
        video_output_path: str, subtitle_settings: dict,
        effect=None, effect_params: dict = None
):
    segments = fix_words(segments)
    vid_capture = cv2.VideoCapture(video_input_path)
    width = int(vid_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vid_capture.get(cv2.CAP_PROP_FPS)

    output_video = cv2.VideoWriter(
        video_output_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, (width, height)
    )

    subtitle_stream = SubtitleStream(
        segments, width, height, fps, subtitle_settings, effect, effect_params
    )

    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            output_video.write(subtitle_stream(frame))
        else:
            break


if __name__ == '__main__':
    from config import PRESETS
    import json
    from effects import fade_effect, bouncing_effect, words_lead_effect

    test_video_path = "test_video/IMG_2073.MOV"
    out_video_path = "test_video/test_22.mp4"
    result_path = "test_video/test_2.json"
    with open(result_path, "r") as t:
        result = json.load(t)

    preset = PRESETS["default"]

    # render_subtitles(
    #     result["data"]["segments"], test_video_path, out_video_path, preset,
    #     fade_effect, {"fadein": 0.1, "fadeout": 0.1}
    # )

    render_subtitles(
        result["data"]["segments"], test_video_path, out_video_path, preset,
        [fade_effect, words_lead_effect], [
            {"fadein": 0.25, "fadeout": 0.25},
            {"karaoke": True}
        ]
    )
