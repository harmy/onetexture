#coding=gbk
import os
import re
import shutil
import struct
import subprocess
import math

CONVERT_CMD_PATH = os.path.dirname(__file__)
CONVER_CMD = os.path.join(CONVERT_CMD_PATH, "convert.exe")
MOGRIFY_CMD = os.path.join(CONVERT_CMD_PATH, "mogrify.exe")
MONTAGE_CMD = os.path.join(CONVERT_CMD_PATH, "montage.exe")
IDENTIFY_CMD = os.path.join(CONVERT_CMD_PATH, "identify.exe")
RES_PATH = os.path.join(os.path.dirname(__file__), "Res")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "Output")
TMP_PATH = os.path.join(RES_PATH, "Tmp")

def init_dirs():
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)
    
def get_matrix(frame_count):
    rows = cols = int(math.sqrt(frame_count))
    while rows * cols < frame_count:
        rows += 1
    return rows, cols

def generate_tbe_file(asset_path, tbe_filename):
    frames = [frame_file for frame_file in os.listdir(asset_path) if frame_file.endswith(".png")]
    frame_count = len(frames)
    frame_data = {}
    for frame in frames:
        output = subprocess.check_output(IDENTIFY_CMD + " -format '%%w,%%h,%%g' %s" % frame)
        pattern = re.compile(r'(\d+),(\d+),(\d+)x(\d+)([\+\-]\d+)([\+\-]\d+)')
        frame_width, frame_height, raw_image_width, raw_image_height, offset_x, offset_y = [int(item) for item in pattern.search(output).groups()]
        frame_data[frame] = {"frame_width" : frame_width, "frame_height" : frame_height,
                             "raw_image_width" : raw_image_width, "raw_image_height" : raw_image_height,
                             "offset_x" : offset_x, "offset_y" : offset_y}
    rows, cols = get_matrix(frame_count)
    frame_idx = 0
    anchor_y = 0
    for row_idx in range(rows):
        anchor_x = 0
        max_height = 0
        for col_idx in range(cols):
            if frame_idx >= frame_count:
                break
            current_frame = frames[frame_idx]
            frame_data[current_frame]["frame_idx"] = frame_idx
            frame_data[current_frame]["lt_x"] = anchor_x
            frame_data[current_frame]["lt_y"] = anchor_y
            frame_data[current_frame]["rb_x"] = anchor_x + frame_data[current_frame]["frame_width"]
            frame_data[current_frame]["rb_y"] = anchor_y + frame_data[current_frame]["frame_height"]
            if max_height < frame_data[current_frame]["frame_height"]:
                max_height = frame_data[current_frame]["frame_height"]
            anchor_x += frame_data[current_frame]["frame_width"]
            frame_idx += 1
        anchor_y += max_height

    with open(tbe_filename, "wb") as f:
        f.write(struct.pack("3h", frame_data[frames[0]]["raw_image_width"], frame_data[frames[0]]["raw_image_height"], frame_count))
        for idx in range(frame_count):
            current_frame = frame_data[frames[idx]]
            f.write(struct.pack("8h", current_frame["frame_idx"], current_frame["offset_x"], current_frame["offset_y"],
                                0, current_frame["lt_x"], current_frame["lt_y"], current_frame["rb_x"], current_frame["rb_y"]))