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

# Regular expression to match display math mode in LaTeX
PATTERNS = [
    r"\\begin\{equation\}(.*?)\\end\{equation\}",          # \begin{equation} ... \end{equation}
    r"\$\$(.*?)\$\$",                                      # $$ ... $$
    r"\\\[(.*?)\\\]",                                      # \[ ... \]
    r"\\\((.*?)\\\)",                                      # \( ... \)
    r"\\begin\{align\}(.*?)\\end\{align\}",                # \begin{align} ... \end{align}
    r"\\begin\{gather\}(.*?)\\end\{gather\}",              # \begin{gather} ... \end{gather}
    r"\\begin\{multline\}(.*?)\\end\{multline\}",          # \begin{multline} ... \end{multline}
    r"\\begin\{split\}(.*?)\\end\{split\}",                # \begin{split} ... \end{split}
    r"\\begin\{flalign\*\}(.*?)\\end\{flalign\*\}",        # \begin{flalign*} ... \end{flalign*}
    r"\\begin\{alignat\}\{\d+\}(.*?)\\end\{alignat\}",     # \begin{alignat}{n} ... \end{alignat}
    r"\\begin\{gathered\}(.*?)\\end\{gathered\}",          # \begin{gathered} ... \end{gathered}
]

# Regular expression to match full text of display math mode in LaTeX
FULLEQU_PATTERNS = [
    r"\\begin\{equation\}.*?\\end\{equation\}",          # \begin{equation} ... \end{equation}
    r"\$\$.*?\$\$",                                      # $$ ... $$
    r"\\\[.*?\\\]",                                      # \[ ... \]
    r"\\\(.*?\\\)",                                      # \( ... \)
    r"\\begin\{align\}.*?\\end\{align\}",                # \begin{align} ... \end{align}
    r"\\begin\{gather\}.*?\\end\{gather\}",              # \begin{gather} ... \end{gather}
    r"\\begin\{multline\}.*?\\end\{multline\}",          # \begin{multline} ... \end{multline}
    r"\\begin\{split\}.*?\\end\{split\}",                # \begin{split} ... \end{split}
    r"\\begin\{flalign\*\}.*?\\end\{flalign\*\}",        # \begin{flalign*} ... \end{flalign*}
    r"\\begin\{alignat\}\{\d+\}.*?\\end\{alignat\}",     # \begin{alignat}{n} ... \end{alignat}
    r"\\begin\{gathered\}.*?\\end\{gathered\}",          # \begin{gathered} ... \end{gathered}
]

LONG_MATH_PATTERNS = r"(\\begin\{equation\}|\$\$|\\\[|\\\(|\\begin\{align\}|\\begin\{gather\}|\\begin\{multline\}|\\begin\{split\}|\\begin\{flalign\*\}|\\begin\{alignat\}\{\d+\}|\\begin\{gathered\})(.*?)(\\end\{equation\}|\$\$|\\\]|\\\)|\\end\{align\}|\\end\{gather\}|\\end\{multline\}|\\end\{split\}|\\end\{flalign\*\}|\\end\{alignat\}|\\end\{gathered\})"

# define the header of tex file
TEX_HEADER_PATTERS = r"\\documentclass.*"

DIR = "workspace"

def compare_jpgs(file1_path, file2_path):
    img1 = Image.open(file1_path)
    img2 = Image.open(file2_path)

    try: 
        diff = ImageChops.difference(img1, img2)

        if diff.getbbox() is None:
            # 图片间没有任何不同则直接退出
            print("【+】We are the same!")
        else:
            print(diff)
            print(diff.getbbox())
            print(diff.getcolors())
            
            # 获取差异区域的左上角坐标
            bbox = diff.getbbox()
            x1, y1, x2, y2 = bbox

            print("左上角坐标1：({}, {})".format(x1, y1))

            # 剔除第一个差异区域，重新查找第二个差异区域
            diff2 = ImageChops.add(diff, diff)
            diff2 = ImageChops.add(diff2, Image.new('RGB', diff.size, (0, 0, 0)))
            bbox2 = diff2.getbbox()

            if bbox2 is not None:
                x1_2, y1_2, x2_2, y2_2 = bbox2
                print("左上角坐标2：({}, {})".format(x1_2, y1_2))
            
            # 保存差异图像
            diff.save('workspace/tmp/'+osp.basename(file2_path))
            diff2.save('workspace/tmp1/'+osp.basename(file2_path))
    except ValueError as e:
        text = ("表示图片大小和box对应的宽度不一致，参考API说明：Pastes another image into this image."
                "The box argument is either a 2-tuple giving the upper left corner, a 4-tuple defining the left, upper, "
                "right, and lower pixel coordinate, or None (same as (0, 0)). If a 4-tuple is given, the size of the pasted "
                "image must match the size of the region.使用2纬的box避免上述问题")
        print("【{0}】{1}".format(e,text))

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

def pdftoimage(pdf_file, img_path):
    if not pdf2image.convert_from_path(pdf_file, output_folder=img_path, fmt="jpeg", dpi=300):
        print(f"Could not create images of {pdf_file}")
    # image_list = sorted(images.glob("*.jpg"))

def remove_temp_files(directory_path):
    files = os.listdir(directory_path)
    for file_name in files:
        if not file_name.endswith(".tex"):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

def remove_substring(original_string, substring_to_remove):
    new_string = original_string.replace(substring_to_remove, '')
    return new_string

def rewirte_header(match):
    # match the header of tex file
    header_str = re.search(TEX_HEADER_PATTERS, match)
    with open("texfile/myhighlight.txt", "r") as file:
        myhighlight = file.read()
    return match[:header_str.end()] + "\n" + myhighlight + "\n" + match[header_str.end():]

def rewrite_math_mode(match, prefix, suffix):
    # 目前 test 得到的情况是
    # original:
    # \begin{tcolorbox}[colframe=white,colback=white]
    # \begin{equation}
    # ...
    # \end{equation}
    # \end{tcolorbox}
    # ----------------------------------------------------
    # modified:
    # \begin{tcolorbox}[colframe=white,colback=black]
    # \begin{equation}
    # ...
    # \end{equation}
    # \end{tcolorbox}
    match = remove_substring(match, "\eqno")
    ##########################################################
    # return r"\begin{empheq}[box=\colorbox{myred}]{equation}" + match + r"\end{empheq}"
    ##########################################################
    return prefix + r"\myboxmath{" + match + r"}" + suffix

def regenerate_latex(texfile, NOWDIR):
    # 读取源文件内容
    texfile = osp.realpath(texfile)
    with open(texfile, "r") as file:
        latex_content = file.read()

    # # 使用正则表达式匹配所有数学公式
    # math_mode_matches = re.findall(LONG_MATH_PATTERNS, latex_content, re.DOTALL)
    # print(math_mode_matches)
    # print('------------------')

    # 对匹配到的数学公式进行处理并写入新文件
    highlight_formulas_filename = osp.splitext(osp.basename(texfile))[0]
    highlight_formulas_filename = osp.join(NOWDIR, highlight_formulas_filename + ".new.tex")

    with open(highlight_formulas_filename, "w") as new_file:
        last_end = 0
        for match in re.finditer(LONG_MATH_PATTERNS, latex_content, re.DOTALL):
            start = match.start()
            if last_end == 0:
                new_file.write(rewirte_header(latex_content[last_end:start]))
            else:
                new_file.write(latex_content[last_end:start])
            new_file.write(rewrite_math_mode(match=match.group(2),prefix=match.group(1),suffix=match.group(3)))
            last_end = match.end()

        new_file.write(latex_content[last_end:])

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

# ----------------------------------------------------------------------------------
# import re

# # Regular expression to match full text of display math mode in LaTeX
# FULLEQU_PATTERNS = [
#     r"\\begin\{equation\}.*?\\end\{equation\}",          # \begin{equation} ... \end{equation}
#     r"\$\$.*?\$\$",                                      # $$ ... $$
#     r"\\\[.*?\\\]",                                      # \[ ... \]
#     r"\\\(.*?\\\)",                                      # \( ... \)
#     r"\\begin\{align\}.*?\\end\{align\}",                # \begin{align} ... \end{align}
#     r"\\begin\{gather\}.*?\\end\{gather\}",              # \begin{gather} ... \end{gather}
#     r"\\begin\{multline\}.*?\\end\{multline\}",          # \begin{multline} ... \end{multline}
#     r"\\begin\{split\}.*?\\end\{split\}",                # \begin{split} ... \end{split}
#     r"\\begin\{flalign\*\}.*?\\end\{flalign\*\}",        # \begin{flalign*} ... \end{flalign*}
#     r"\\begin\{alignat\}\{\d+\}.*?\\end\{alignat\}",     # \begin{alignat}{n} ... \end{alignat}
#     r"\\begin\{gathered\}.*?\\end\{gathered\}",          # \begin{gathered} ... \end{gathered}
# ]

# def add_prefix_to_math_mode(match):
#     return "AAA" + match

# def main():
#     # 读取源文件内容
#     with open("texfile/test1.tex", "r") as file:
#         latex_content = file.read()

#     # 使用正则表达式匹配所有数学公式
#     math_mode_matches = re.findall("|".join(FULLEQU_PATTERNS), latex_content, re.DOTALL)
#     print(math_mode_matches)

#     # 对匹配到的数学公式进行处理并写入新文件
#     with open("test1.new.tex", "w") as new_file:
#         last_end = 0
#         for match in math_mode_matches:
#             start = latex_content.find(match, last_end)
#             new_file.write(latex_content[last_end:start])
#             new_file.write(add_prefix_to_math_mode(match))
#             last_end = start + len(match)

#         new_file.write(latex_content[last_end:])

# if __name__ == "__main__":
#     main()