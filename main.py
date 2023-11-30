from core import SubtitleStream

import cv2

import queue
import threading


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


def run_subtitle(sub, i, frame, out_queue):
    out_queue.put((i, sub(i, frame)))


def queue_thread(q, subtitle_stream, out_queue):
    while True:
        i, frame = q.get()
        sub = subtitle_stream.get_sub(i)
        if sub is None:
            out_queue.put((i, frame))
        else:
            threading.Thread(target=run_subtitle, args=(sub, i, frame, out_queue,)).start()


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

    i = 0

    main_queue = queue.Queue()
    out_queue = queue.Queue()
    main_threads = [
        threading.Thread(target=queue_thread, args=(main_queue, subtitle_stream, out_queue), daemon=True).start()
        for _ in range(12)
    ]

    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            main_queue.put((i, frame))
            i += 1
        else:
            break

    out_frames = []

    while len(out_frames) < i:
        inp = out_queue.get()
        out_frames.append(inp)

    out_frames = sorted(out_frames, key=lambda x: x[0], reverse=True)

    for _, frame in out_frames:
        output_video.write(frame)


if __name__ == '__main__':
    from themes import THEMES
    import json
    import time

    test_video_path = "test_video/IMG_2073.MOV"
    out_video_path = "test_video/test_2s56.mp4"
    result_path = "test_video/test_2.json"
    with open(result_path, "r") as t:
        result = json.load(t)

    preset = THEMES["HORMOZI 3"]
    start_time = time.time()
    render_subtitles(
        result["data"]["segments"], test_video_path, out_video_path, preset
    )
    print(time.time() - start_time)
