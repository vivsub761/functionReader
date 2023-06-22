from moviepy.editor import ImageClip, concatenate_videoclips
import cv2
import pytesseract
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Python script to convert manga pages to video format")
parser.add_argument("-d", "--targetDirectory", help="Directory that contains the pages that will be converted to a video")
parser.add_argument("-f", "--frameTime", help = "Time each frame should stay on screen", default = 3)
args = parser.parse_args()

# custom sort key to sort the pages correctly(see below for proper format)
def sortkey(filename):
    i = len(filename) - 1
    while filename[i] != "/":
        i -= 1
    filename = filename[i + 1:]

    j = 0
    while filename[j] != "_" and filename[j] != ".":
        j += 1
    if filename[j] == ".":
        return int(filename[:j])
    num1 = filename[:j]
    while filename[j] != ".":
        j += 1
    num2 = filename[len(num1) + 1: j]
    return [int(num1), int(num2)]

pages = []

# iterate through page directory to get a list of all the names of the files
for filename in os.listdir(args.targetDirectory):
    pages.append(args.targetDirectory + "/" + filename)

# sort the pages
# IMPORTANT: pages in the directory MUST be in the form "pageNumber_frameNumber.extension or chronologicalNumber.extension"
pages.sort(key = sortkey)
frame_time = int(args.frameTime)
video_clips = []
start_time = 0
for filename in pages:
    # Load image as a video clip
    image_clip = ImageClip(filename)

    # create a cv2 image from the file
    image = cv2.imread(filename)
    # fade between frames
    fade_duration = 1

    # Don't fade in before first image
    if start_time > 0:
        image_clip = image_clip.fadein(fade_duration)

    # set frame into video
    image_clip = image_clip.set_duration(frame_time).set_start(start_time)
    # fade out
    image_clip = image_clip.fadeout(fade_duration)
    # add image clip to video
    video_clips.append(image_clip)
    # change start time to appropriate time for new frame
    start_time += frame_time

# concatenate clips into a full video
final_video = concatenate_videoclips(video_clips, "compose")


outputPath = "outputVideo.mp4"

# write final video 
final_video.write_videofile(outputPath, codec="mpeg4", fps=30)


