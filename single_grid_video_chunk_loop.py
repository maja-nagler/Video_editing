import os
import re
import numpy as np
from datetime import timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image, ImageDraw

# === Monkey-patch PIL for compatibility with MoviePy ===
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# === USER CONFIGURATION ===
VIDEO_DIR = "./Volumes/Lexar/Clips"
SCREENSHOT_DIR = os.path.join(VIDEO_DIR, "screenshots")
CLIP_DIR = os.path.join(VIDEO_DIR, "30_second_video_segment")
CLIP_DURATION = 30  # seconds
INTERVAL = 5 * 60   # every 5 minutes
OUTPUT_HEIGHT = 1080
OUTPUT_FPS = 15

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(CLIP_DIR, exist_ok=True)

## Extracting timestamp from filename
def extract_timestamp(filename):
    match = re.search(r"DJI_(\d{14})_", filename)
    if match:
        return match.group(1)
    return "00000000000000"

## Sorting video files based on the extracted timestamp
mp4_files = [
    f for f in os.listdir(VIDEO_DIR)
    if f.lower().endswith(".mp4") and not f.startswith("._")
]
mp4_files_sorted = sorted(mp4_files, key=extract_timestamp)

print("Ordered list of MP4 files in the folder by timestamp:")
for f in mp4_files_sorted:
    print("  -", f)

## Loading clips and durations
clips = []
clip_durations = []
for f in mp4_files_sorted:
    path = os.path.join(VIDEO_DIR, f)
    clip = VideoFileClip(path)
    clips.append(clip)
    clip_durations.append(clip.duration)

## Concatenate all video clips
full_video = concatenate_videoclips(clips, method="compose")

rotate_deg = int(input("🔄 Rotate videos/snapshots by how many degrees? (e.g. 270): "))
custom_start = int(input("⏱️ Enter start time (in seconds) for FIRST screenshot/video clip:  "))

## Unifying grid overlay using PIL (for images and video frames)
def add_grid_overlay(image, grid_rows=3, grid_cols=3, line_color=(80, 80, 80), line_width=2):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for i in range(1, grid_cols):
        x = i * width / grid_cols
        draw.line([(x, 0), (x, height)], fill=line_color, width=line_width)
    for i in range(1, grid_rows):
        y = i * height / grid_rows
        draw.line([(0, y), (width, y)], fill=line_color, width=line_width)
    return image

##Adding grid overlay to each frame in the video (MoviePy and PIL)

## To change the grid color, change the line color values e.g. https://www.w3schools.com/colors/colors_shades.asp
def add_grid_to_clip(clip, grid_rows=3, grid_cols=3, line_color=(80, 80, 80), line_width=2):
    def apply_grid(frame):
        img = Image.fromarray(frame)
        img = add_grid_overlay(img, grid_rows, grid_cols, line_color, line_width)
        return np.array(img)
    return clip.fl_image(apply_grid)

##  Determining the next available index number
def get_next_index(folder, prefix, ext):
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(ext)]
    nums = [int(re.search(r'_no_(\d+)', f).group(1)) for f in files if re.search(r'_no_(\d+)', f)]
    return max(nums) + 1 if nums else 1

screenshot_index = get_next_index(SCREENSHOT_DIR, "screen", ".jpg")
clip_index = get_next_index(CLIP_DIR, "clip", ".mp4")

## Main loop 
for t in range(custom_start, int(full_video.duration), INTERVAL):
    end_sec = min(t + CLIP_DURATION, full_video.duration)

    cumulative = 0
    for i, dur in enumerate(clip_durations):
        if t < cumulative + dur:
            source_index = i
            time_within_chunk = t - cumulative
            break
        cumulative += dur

    hms = str(timedelta(seconds=round(time_within_chunk))).replace(":", "").zfill(6)[-6:]

    timestamp_str = hms
    source_file = mp4_files_sorted[source_index]
    source_id = re.search(r"_(\d{4})_", source_file)
    source_id_str = source_id.group(1) if source_id else f"{source_index:04d}"

    # Screenshot processing
    frame = full_video.get_frame(t)
    img = Image.fromarray(frame).convert("RGB").rotate(rotate_deg, expand=True)
    img = add_grid_overlay(img)
    screenshot_name = os.path.join(
        SCREENSHOT_DIR,
        f"screen{screenshot_index}_timestamp_{timestamp_str}_source_index_{source_id_str}_no_{screenshot_index:04d}.jpg"
    )
    img.save(screenshot_name)
    print(f"Saved {os.path.basename(screenshot_name)}")
    screenshot_index += 1

    # Video processing
    subclip = (
        full_video.subclip(t, end_sec)
        .rotate(rotate_deg)
        .resize(height=OUTPUT_HEIGHT)
        .set_fps(OUTPUT_FPS)
    )
    subclip_with_grid = add_grid_to_clip(subclip)

    final_clip_path = os.path.join(
        CLIP_DIR,
        f"clip{clip_index}_timestamp_{timestamp_str}_source_index_{source_id_str}_no_{clip_index:04d}.mp4"
    )
    subclip_with_grid.write_videofile(final_clip_path, codec="libx264", audio=False, verbose=False, logger=None)
    print(f"Saved {os.path.basename(final_clip_path)}")
    clip_index += 1

for clip in clips:
    clip.close()
full_video.close()

print("Videos processed with grid overlays.")
