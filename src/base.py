import re
import shutil
import subprocess
import sys
import os
import os.path as osp
import glob
import time
from compile_pdf import compile_pdf
from crop_bbox import crop_bbox, show_bbox
from coco_json import convert_and_save_coco_format
from pdf2imgs import pdftoimage
from regen_latex import regenerate_latex
from utils import remove_folder, remove_temp_files
import pdf2image
from PIL import Image, ImageChops
from cmp_imgs import cmp_imgs
import tqdm

ROOTDIR = "workspace"
CATEGORIES_DICT = {"formula": 1}

def main(folder):
    if folder.endswith("/"):
        folder = folder[:-1]
    texfile = sorted(glob.glob(folder + "/*.tex"))
    # get now time to make a new folder
    now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    # now = '2023-08-09-12-01-14' # debug
    NOWDIR = osp.join(ROOTDIR, now)
    os.makedirs(NOWDIR, exist_ok=True)
    # make folders to store the source tex file and the new tex file, and the generated pdf respectively
    # -------------------------------------------------------
    ORIGINAL_ROOT_FOLDER = osp.join(NOWDIR, "original")
    MODIFIED_ONE_ROOT_FOLDER = osp.join(NOWDIR, "modified_one")
    MODIFIED_TWO_ROOT_FOLDER = osp.join(NOWDIR, "modified_two")
    DIFF_ROOT_FOLDER = osp.join(NOWDIR, "diff")

    ORIGINAL_LATEX_FOLDER = osp.join(ORIGINAL_ROOT_FOLDER, "latex")
    MODIFIED_ONE_LATEX_FOLDER = osp.join(MODIFIED_ONE_ROOT_FOLDER, "latex")
    MODIFIED_TWO_LATEX_FOLDER = osp.join(MODIFIED_TWO_ROOT_FOLDER, "latex")

    MODIFIED_ONE_PDF_FOLDER = osp.join(MODIFIED_ONE_ROOT_FOLDER, "pdf")
    MODIFIED_TWO_PDF_FOLDER = osp.join(MODIFIED_TWO_ROOT_FOLDER, "pdf")

    MODIFIED_ONE_IMGS_FOLDER = osp.join(MODIFIED_ONE_ROOT_FOLDER, "imgs")
    MODIFIED_TWO_IMGS_FOLDER = osp.join(MODIFIED_TWO_ROOT_FOLDER, "imgs")
    DIFF_IMGS_FOLDER = osp.join(DIFF_ROOT_FOLDER, "imgs")

    MODIFIED_ONE_TMP_FOLDER = osp.join(MODIFIED_ONE_ROOT_FOLDER, "tmp")
    MODIFIED_TWO_TMP_FOLDER = osp.join(MODIFIED_TWO_ROOT_FOLDER, "tmp")

    DIFF_ANNOS_FOLDER = osp.join(DIFF_ROOT_FOLDER, "annos")
    # -------------------------------------------------------
    
    os.makedirs(ORIGINAL_ROOT_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_ONE_ROOT_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_TWO_ROOT_FOLDER, exist_ok=True)
    os.makedirs(DIFF_ROOT_FOLDER, exist_ok=True)

    os.makedirs(ORIGINAL_LATEX_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_ONE_LATEX_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_TWO_LATEX_FOLDER, exist_ok=True)

    os.makedirs(MODIFIED_ONE_PDF_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_TWO_PDF_FOLDER, exist_ok=True)

    os.makedirs(MODIFIED_ONE_IMGS_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_TWO_IMGS_FOLDER, exist_ok=True)
    os.makedirs(DIFF_IMGS_FOLDER, exist_ok=True)

    os.makedirs(MODIFIED_ONE_TMP_FOLDER, exist_ok=True)
    os.makedirs(MODIFIED_TWO_TMP_FOLDER, exist_ok=True)

    os.makedirs(DIFF_ANNOS_FOLDER, exist_ok=True)
    # -------------------------------------------------------

    # copy all the source tex file to new folder
    # for tex in texfile:
    #     shutil.copy(src=tex, dst=ORIGINAL_LATEX_FOLDER)
    print("[INFO] copy all the source tex file to new folder")
    os.system("cp " + folder + "/*.tex " + ORIGINAL_LATEX_FOLDER)
    print("[INFO] copy all the source tex file to new folder done")

    # regenerate the tex file
    print("[INFO] regenerate the tex file")
    for tex in texfile:
        print('processing to regenerate {}'.format(tex))
        regenerate_latex(texfile=tex, NEWDIR=MODIFIED_ONE_TMP_FOLDER, mode=0)
        regenerate_latex(texfile=tex, NEWDIR=MODIFIED_TWO_TMP_FOLDER, mode=1)
    print("[INFO] regenerate the tex file done")

    # compile the tex file to pdf
    print("[INFO] compile the tex file to pdf")
    # compile each file with 120s waiting time and use tqdm
    for tex in tqdm.tqdm(sorted(glob.glob(MODIFIED_ONE_TMP_FOLDER + "/*.tex"))):
        # print("now compile {}".format(tex))
        compile_pdf(source_dir=MODIFIED_ONE_TMP_FOLDER, each_waiting_time=20, source_file=tex)
    for tex in tqdm.tqdm(sorted(glob.glob(MODIFIED_TWO_TMP_FOLDER + "/*.tex"))):
        # print("now compile {}".format(tex))
        compile_pdf(source_dir=MODIFIED_TWO_TMP_FOLDER, each_waiting_time=20, source_file=tex)
    print("[INFO] compile the tex file to pdf done")

    # copy the pdf file to new folder
    print("[INFO] copy the pdf file to new folder and the tex file to new folder")
    os.system("cp " + MODIFIED_ONE_TMP_FOLDER + "/*.pdf " + MODIFIED_ONE_PDF_FOLDER)
    os.system("cp " + MODIFIED_TWO_TMP_FOLDER + "/*.pdf " + MODIFIED_TWO_PDF_FOLDER)
    os.system("cp " + MODIFIED_ONE_TMP_FOLDER + "/*.tex " + MODIFIED_ONE_LATEX_FOLDER)
    os.system("cp " + MODIFIED_TWO_TMP_FOLDER + "/*.tex " + MODIFIED_TWO_LATEX_FOLDER)
    print("[INFO] copy the pdf file to new folder and the tex file to new folder done")
    
    # remove the temp files not end with .tex
    print("[INFO] remove the temp folder")
    remove_folder(MODIFIED_ONE_TMP_FOLDER)
    remove_folder(MODIFIED_TWO_TMP_FOLDER)
    print("[INFO] remove the temp folder done")

    # convert the pdf files to images
    print("[INFO] convert the pdf files to images")
    for pdf in sorted(glob.glob(MODIFIED_ONE_PDF_FOLDER + "/*.pdf")):
        # get the basename
        basename = osp.basename(pdf)
        print(basename)
        print(osp.splitext(basename)[0])
        img_path = osp.join(MODIFIED_ONE_IMGS_FOLDER, osp.splitext(basename)[0])
        os.makedirs(img_path, exist_ok=True)
        if not pdftoimage(pdf, img_path=img_path):
            os.system('rm -rf ' + img_path)
    print("[INFO] convert the pdf files to images half done")
    for pdf in sorted(glob.glob(MODIFIED_TWO_PDF_FOLDER + "/*.pdf")):
        # get the basename
        basename = osp.basename(pdf)
        img_path = osp.join(MODIFIED_TWO_IMGS_FOLDER, osp.splitext(basename)[0])
        os.makedirs(img_path, exist_ok=True)
        if not pdftoimage(pdf, img_path=img_path):
            os.system('rm -rf ' + img_path)
    print("[INFO] convert the pdf files to images done")

    # generate the annotation file
    ## find the id of each latex file, this could be found by the name of the imgs folders
    print("[INFO] generate the annotation file for the successful generated images")
    latex_id_list = []
    for img_folder in sorted(glob.glob(MODIFIED_ONE_IMGS_FOLDER + "/*")):
        latex_id_list.append(osp.basename(img_folder))
        img_path = osp.join(DIFF_IMGS_FOLDER, osp.basename(img_folder))
        annos_path = osp.join(DIFF_ANNOS_FOLDER, osp.basename(img_folder))
        os.makedirs(img_path, exist_ok=True)
        os.makedirs(annos_path, exist_ok=True)
    ## for each latex_id, we find the corresponding imgs and compare them
    for id in latex_id_list:
        img1_list = glob.glob(MODIFIED_ONE_IMGS_FOLDER + "/" + id + "/*.jpg")
        img2_list = glob.glob(MODIFIED_TWO_IMGS_FOLDER + "/" + id + "/*.jpg")
        img1_list = sorted(img1_list)
        img2_list = sorted(img2_list)
        for img1, img2 in zip(img1_list, img2_list):
            print('-' * 88)
            print('now compare {} {} {}'.format(id, img1, img2))
            bboxes = cmp_imgs(img1,img2)
            diff_img_path = osp.join(DIFF_IMGS_FOLDER, id, osp.splitext(osp.basename(img1))[0] + ".jpg")
            diff_anno_path = osp.join(DIFF_ANNOS_FOLDER, id, osp.splitext(osp.basename(img1))[0] + ".json")
            if bboxes:
                print('the bboxes are {}'.format(bboxes))
                print('now crop the bbox')
                bboxes = crop_bbox(img1, bboxes)
                show_bbox(img1, bboxes, diff_img_path)
                # write the annotation file
                convert_and_save_coco_format(image_path=img1, bbox_list=bboxes, category_list=["formula"] * len(bboxes), category_meta_dict=CATEGORIES_DICT, save_json_file_path=diff_anno_path)
            else:
                print('no bbox found')
                show_bbox(img1, bboxes, diff_img_path)
                # write the annotation file
                convert_and_save_coco_format(image_path=img1, bbox_list=bboxes, category_list=None, category_meta_dict=CATEGORIES_DICT, save_json_file_path=diff_anno_path)
            print('-' * 88)
    print("[INFO] generate the annotation file for the successful generated images done")


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