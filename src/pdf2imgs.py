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

DPI = 500
def pdftoimage(pdf_file, img_path):
    try:
        images = pdf2image.convert_from_path(pdf_file, output_folder=img_path, fmt="jpeg", dpi=DPI)
        if not images:
            print(f"Could not create images from {pdf_file}")
        # else:
            # print(f"Successfully created images from {pdf_file}")
    except pdf2image.exceptions.PDFPageCountError as e:
        print(f"PDFPageCountError: \n{e}Could not convert {pdf_file} to images.")
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: pdf2imgs pdf imgs_folder\n"+    
              "select one pdf and one imgs_folder to convert\n")
    elif len(sys.argv) == 3:
        pdftoimage(sys.argv[1],sys.argv[2])