#coding=gbk
from common import *

ACTIONS = {"001" : "待机"}

def main():    
    for dir in os.listdir(os.path.join(RES_PATH, "NPC")):
        shape, name = dir.split("_")
        shape = int(shape)
        for key, value in ACTIONS.iteritems():
            dest_dir = os.path.join(OUTPUT_PATH, dir)
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            dest_filename = os.path.join(dest_dir, "00%04d%s.png" % (shape, key))
            if os.path.exists(dest_filename):
                print "%s已存在, 跳过该文件." % dest_filename
                continue
            src_dir = os.path.join(RES_PATH, "NPC", dir, value)
            if not os.path.exists(src_dir):
                continue
            print "正在转换: %s ..." % dest_filename
            tmp_dir = os.path.join(TMP_PATH, "NPC", dir, value)
            shutil.copytree(src_dir, tmp_dir)
            os.chdir(tmp_dir)
            frames = [frame_file for frame_file in os.listdir(tmp_dir) if frame_file.endswith(".png")]
            frame_count = len(frames)
            rows, cols = get_matrix(frame_count)
            os.system(MOGRIFY_CMD + " -trim *.png")
            os.system(MONTAGE_CMD + " *.png -tile %dx%d -geometry +0+0 -gravity North -background none %s" % (cols, rows, dest_filename))
            generate_tbe_file(tmp_dir, dest_filename.replace(".png", ".tbe"))
        os.chdir(dest_dir)
        os.system(MOGRIFY_CMD + " -depth 6 *.png")
        
if __name__ == "__main__":
    init_dirs()
    main()
