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

def compile_pdf(source_dir, each_waiting_time, source_file):
    """Compile source directory."""
    if source_dir is None:
        return False
    source_file = osp.basename(source_file)
    # increase time by the number of latex files under source_dir
    # waiting_time = each_waiting_time * len(glob.glob(source_dir + "/*.tex"))

    # if source_dir.is_file():
    #     source_dir = source_dir.parent

    try:
        latexmk = subprocess.Popen(["latexmk", "-pdflatex", "-interaction=nonstopmode", "-quiet", "-f", source_file], cwd=source_dir,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if latexmk.returncode == 0:
            return True
        # latexmk.wait(timeout=each_waiting_time)
    except Exception as e:
        print("Error occurred while calling the process:", str(e))

# test
if __name__ == "__main__":
    # read the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True, help="folder path to the latex file")
    parser.add_argument("-f", "--file", required=True, help="file name of the latex file")
    parser.add_argument("-w", "--waiting", required=False, type=float, default=120, help="waiting time for compiling the latex file")
    args = parser.parse_args()
    # compile the latex file
    compile_pdf(args.source, args.waiting, args.file)