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
    frame = sub(i, frame)
    out_queue.put((i, frame))


def queue_thread(q, subtitle_stream, out_queue):
    while True:
        i, frame = q.get()
        sub = subtitle_stream.get_sub(i)
        if sub is None:
            out_queue.put((i, frame))
        else:
            threading.Thread(target=run_subtitle, args=(sub, i, frame, out_queue,), daemon=True).start()


def write_thread(output_video, out_queue: queue.Queue, length):
    i = 0
    out_frames = []
    while True:
        i_, frame = out_queue.get()

        if i_ == i:
            output_video.write(frame)
            del frame
            i += 1
        else:
            out_frames.append((i_, frame))

        if len(out_frames) > 0 and not len(out_frames) % 50:
            out_frames = sorted(out_frames, key=lambda x: x[0], reverse=False)

        while len(out_frames) and out_frames[0][0] == i:
            j, frame = out_frames.pop(0)
            output_video.write(frame)
            del frame
            i += 1

        if i >= length:
            break


def render_subtitles(
        segments: list[dict], video_input_path: str,
        video_output_path: str, subtitle_settings: dict
):
    vid_capture = cv2.VideoCapture(video_input_path)
    width = int(vid_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vid_capture.get(cv2.CAP_PROP_FPS)
    length = int(vid_capture.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    output_video = cv2.VideoWriter(
        video_output_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, (width, height)
    )

    subtitle_stream = SubtitleStream(
        segments, width, height, fps, subtitle_settings
    )

    i = 0

    main_queue = queue.Queue()
    out_queue = queue.Queue()
    [
        threading.Thread(target=queue_thread, args=(main_queue, subtitle_stream, out_queue), daemon=True).start()
        for _ in range(12)
    ]

    threading.Thread(target=write_thread, args=(output_video, out_queue, length, ), daemon=True).start()

    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            main_queue.put((i, frame))
            i += 1
            if main_queue.qsize() > 500:
                time.sleep(0.1)
        else:
            break


if __name__ == '__main__':
    from themes import THEMES
    import json
    import time

    # test_video_path = "test_video/IMG_2073.MOV"
    # out_video_path = "test_video/test_2s5116.mp4"
    # result_path = "test_video/test_2.json"

    test_video_path = "/home/jjjj/Downloads/Telegram Desktop/Forming the band with Noel Redding and Mitch Mitchell_.mp4"
    out_video_path = "test_video/test_23ss.mp4"
    result_path = "/home/jjjj/Documents/render_subtitles/123sdkalads.json"
    with open(result_path, "r") as t:
        result = json.load(t)

    preset = THEMES["HORMOZI 3"]
    start_time = time.time()
    render_subtitles(
        result["segments"], test_video_path, out_video_path, preset
    )
    print(time.time() - start_time)
