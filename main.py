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
        video_output_path: str, subtitle_settings: dict
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
        segments, width, height, fps, subtitle_settings
    )

    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            output_video.write(subtitle_stream(frame))
        else:
            break


if __name__ == '__main__':
    from themes import THEMES
    import json

    test_video_path = "test_video/IMG_2073.MOV"
    out_video_path = "test_video/test_24.mp4"
    result_path = "test_video/test_2.json"
    with open(result_path, "r") as t:
        result = json.load(t)

    preset = THEMES["HORMOZI 1"]

    # render_subtitles(n
    #     result["data"]["segments"], test_video_path, out_video_path, preset,
    #     fade_effect, {"fadein": 0.1, "fadeout": 0.1}
    # )

    render_subtitles(
        result["data"]["segments"], test_video_path, out_video_path, preset
    )
