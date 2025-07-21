import os
from moviepy.editor import VideoFileClip
from PIL import Image

#Defining path to video file (happy to adjust to a folder with multiple files)
video = VideoFileClip("./fish_video_example.mp4") 

#Defining names of the output folders
os.makedirs("screenshots", exist_ok=True)
os.makedirs("10_second_video_segments", exist_ok=True)

# Interval in seconds (currently 5 minutes, can be changed to any number)
interval = 5 * 60

#Main loop for naming files by the timestamps
for t in range(0, int(video.duration), interval): 
        #Looping through video duration, from 0, increasing by the interval value
    h, m, s = t // 3600, (t % 3600) // 60, t % 60 
        #Converts the current time (in seconds) into hours, minutes, and seconds (for naming the files)
    start = f"{h:02d}-{m:02d}-{s:02d}"
        #Formats the start timestamp for the filename 
    end_sec = min(t + 10, video.duration)
        #Defining end time for the video segment, if longer segments needed 10 can be replaced with a different value
    eh, em, es = int(end_sec) // 3600, (int(end_sec) % 3600) // 60, int(end_sec) % 60
        #Converts the end time end_sec into correct format (h,m,s)
    end = f"{eh:02d}-{em:02d}-{es:02d}"
        #Formats the end timestamp for the filename

    # Code for taking screenshots
    Image.fromarray(video.get_frame(t)).save(f"screenshots/{start}.jpg")

    # Code for generating 10-second video segments 
    video.subclip(t, end_sec).write_videofile(
        f"10_second_video_segments/beg_{start}_end_{end}.mp4",
        codec="libx264", audio=False, verbose=False, logger=None
    )

video.close()
