import re
import shutil
import subprocess
import sys
import os
import os.path as osp
import glob
import time
import pdf2image
from PIL import Image, ImageChops

def pdftoimage(pdf_file, img_path):
    if not pdf2image.convert_from_path(pdf_file, output_folder=img_path, fmt="jpeg", dpi=500):
        print(f"Could not create images of {pdf_file}")
    # image_list = sorted(images.glob("*.jpg"))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: pdf2imgs pdf imgs_folder\n"+    
              "select one pdf and one imgs_folder to convert\n")
    elif len(sys.argv) == 3:
        pdftoimage(sys.argv[1],sys.argv[2])