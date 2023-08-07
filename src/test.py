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

DIR = "workspace"

def main(folder):
    if folder.endswith("/"):
        folder = folder[:-1]
    texfile = glob.glob(folder + "/*.tex")
    # get now time to make a new folder
    now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    NOWDIR = osp.join(DIR, now)
    os.makedirs(NOWDIR)
    # make folders to store the source tex file and the new tex file, and the generated pdf respectively
    SOURCE = osp.join(NOWDIR, "source")
    NEW = osp.join(NOWDIR, "new")
    SOURCE_PDF = osp.join(NOWDIR, "source_pdf")
    NEW_PDF = osp.join(NOWDIR, "new_pdf")
    SOURCE_IMGS = osp.join(NOWDIR, "source_imgs")
    NEW_IMGS = osp.join(NOWDIR, "new_imgs")
    IMG_ANNOS = osp.join(NOWDIR, "img_annos")

    os.makedirs(SOURCE)
    os.makedirs(NEW)
    os.makedirs(SOURCE_PDF)
    os.makedirs(NEW_PDF)
    os.makedirs(SOURCE_IMGS)
    os.makedirs(NEW_IMGS)
    os.makedirs(IMG_ANNOS)

    # copy the source tex file to new folder
    os.system("cp " + folder + "/*.tex " + SOURCE)

    # regenerate the tex file
    for tex in texfile:
        regenerate_latex(tex, NEW)

    # compile the tex file to pdf
    compile_pdf(SOURCE, waiting_time=120)
    compile_pdf(NEW, waiting_time=120)

    # copy the pdf file to new folder
    os.system("cp " + SOURCE + "/*.pdf " + SOURCE_PDF)
    os.system("cp " + NEW + "/*.pdf " + NEW_PDF)

    # remove the temp files not end with .tex
    remove_temp_files(SOURCE)
    remove_temp_files(NEW)

    # convert the pdf files to images
    for pdf in glob.glob(SOURCE_PDF + "/*.pdf"):
        # get the basename
        basename = osp.basename(pdf)
        img_path = osp.join(SOURCE_IMGS, osp.splitext(basename)[0])
        os.makedirs(img_path)
        pdftoimage(pdf, img_path=img_path)
    for pdf in glob.glob(NEW_PDF + "/*.pdf"):
        # get the basename
        basename = osp.basename(pdf)
        img_path = osp.join(NEW_IMGS, osp.splitext(basename)[0])
        os.makedirs(img_path)
        pdftoimage(pdf, img_path=img_path)

    # generate the annotation file
    for img in glob.glob(SOURCE_IMGS + "/*/*.jpg"):
        # get the parent folder
        latex_file_name = osp.basename(osp.dirname(img))
        # print(latex_file_name)   # debug
        # new the folder using the name of the latex file (which is parent_folder here)
        parent_folder = osp.join(IMG_ANNOS,latex_file_name)
        os.makedirs(name=parent_folder,exist_ok=True)
        # get the basename
        basename = osp.basename(img)
        baseid = (osp.splitext(basename)[0]).split('-')[-1]
        compared_filename = 'INIT'
        for cmp_img in glob.glob(NEW_IMGS + "/" +latex_file_name + ".new/*.jpg" ):
            cmpid = (osp.splitext(cmp_img)[0]).split('-')[-1]
            if cmpid == baseid:
                compared_filename = cmp_img
        # print(img, compared_filename) # debug
        # then compare the imgs to find the ground truth
        compare_jpgs(img, compared_filename)
        # copy the img and write to annotation
        destination_file = osp.join(parent_folder, basename)
        shutil.copy(src=img, dst=destination_file)
        img_anno = osp.join(IMG_ANNOS, osp.splitext(basename)[0] + ".txt")
        # open the file, if not exist, new it
        with open(img_anno, "w") as f:
            f.write("0")

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print("usage: latex2formulas folder\n"+    
              "select one folder including tex file to highlight formulas")
    elif len(sys.argv) == 3:
        ori_imgs_list = glob.glob(sys.argv[1]+"*.jpg")
        ori_imgs_list = sorted(ori_imgs_list)
        cmp_imgs_list = glob.glob(sys.argv[2]+"*.jpg")
        cmp_imgs_list = sorted(cmp_imgs_list)
        for img1, img2 in zip(ori_imgs_list, cmp_imgs_list):
            print('-' * 88)
            print('now compare {} {}'.format(img1, img2))
            bboxes = cmp_imgs(img1,img2)
            if bboxes:
                print('the bboxes are {}'.format(bboxes))
                print('now crop the bbox')
            print('-' * 88)
    elif len(sys.argv) == 2:
        main(sys.argv[1])