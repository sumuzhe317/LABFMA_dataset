import argparse
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
from cmp_imgs import cmp_imgs

def compile_pdf(source_dir, waiting_time):
    """Compile source directory."""
    if source_dir is None:
        return False

    # if source_dir.is_file():
    #     source_dir = source_dir.parent

    latexmk = subprocess.Popen(["latexmk", "-pdflatex", "-interaction=nonstopmode", "-quiet", "-f"], cwd=source_dir,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        latexmk.wait(timeout=waiting_time)  # increase time
    except subprocess.TimeoutExpired:
        latexmk.kill()

# test
if __name__ == "__main__":
    # read the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True, help="folder path to the latex file")
    parser.add_argument("-w", "--waiting", required=False, type=float, default=120, help="waiting time for compiling the latex file")
    args = parser.parse_args()
    # compile the latex file
    compile_pdf(args.source, args.waiting)