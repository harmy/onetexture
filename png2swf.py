#coding=gbk
from __future__ import with_statement
from xml.dom.minidom import Document
import os
import shutil
import glob


SRC_PATH = os.path.join(os.path.dirname(__file__), "Output")
DEST_PATH = os.path.join(os.path.dirname(__file__), "Swf")
LATEST_PATH = os.path.join(os.path.dirname(__file__), "Latest")

if not os.path.exists(DEST_PATH):
    os.mkdir(DEST_PATH)
    
if os.path.exists(LATEST_PATH):
    shutil.rmtree(LATEST_PATH)
os.mkdir(LATEST_PATH)

def main():
    png_files = [file for file in glob.glob("%s/*/*.png" % SRC_PATH)]
    pending_files = [file for file in png_files if not os.path.exists(file.replace(".png",".swf").replace("Output", "Swf"))]
    if pending_files == []:
        print "没有需要转换的文件!"
        return
    for file in pending_files:
        xmlTree = Document()
        firstNode = xmlTree.createElement("lib")
        xmlTree.appendChild(firstNode)
        firstNode.setAttribute("allowDomain", "*")
        bitmapdata_node = xmlTree.createElement("bitmapdata")
        bitmapdata_node.setAttribute("file", file)
        bitmapdata_node.setAttribute("compression", "true")
        bitmapdata_node.setAttribute("quality", "65")
        bitmapdata_node.setAttribute("class","bmp_%s" % os.path.basename(file)[:-4])
        firstNode.appendChild(bitmapdata_node)
        bytearray_node = xmlTree.createElement("bytearray")
        bytearray_node.setAttribute("file", file.replace(".png", ".tbe"))
        bytearray_node.setAttribute("class", "tbe_%s" % os.path.basename(file)[:-4])
        firstNode.appendChild(bytearray_node)
        xmlTree.encoding = "UTF-8"
        xml_file = os.path.join(LATEST_PATH, os.path.basename(file).replace(".png",".xml"))
        swf_file = xml_file.replace(".xml",".swf")
        with open(xml_file, "w") as f:
            f.write(xmlTree.toprettyxml().decode("gbk").encode("utf-8"))
        os.system("java -jar Swift.jar xml2lib %s %s" % (xml_file, swf_file))
        dest_path = os.path.dirname(file.replace("Output", "Swf"))
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        shutil.copy(swf_file, dest_path)

if __name__ == "__main__":
    main()