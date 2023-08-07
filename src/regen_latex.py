import argparse
import re
import shutil
import subprocess
import sys
import os
import os.path as osp
import glob
import time
from utils import remove_substring
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

NEW_LATEX_FILE_SUFFIX = ".new.tex"

def rewirte_header(match):
    # match the header of tex file
    header_str = re.search(TEX_HEADER_PATTERS, match)
    with open("texfile/myhighlight.txt", "r") as file:
        myhighlight = file.read()
    return match[:header_str.end()] + "\n" + myhighlight + "\n" + match[header_str.end():]

def rewrite_math_mode(match, prefix, suffix, mode):
    ##########################################################
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
    ##########################################################
    # 废弃方案1
    # return r"\begin{empheq}[box=\colorbox{myred}]{equation}" + match + r"\end{empheq}"
    ##########################################################
    # 废弃方案2
    # match = remove_substring(match, "\eqno")
    # return prefix + r"\myboxmath{" + match + r"}" + suffix
    ##########################################################
    # 方案3
    match = remove_substring(match, "\eqno")
    if mode == 0:
        return prefix + r"\begin{tcolorbox}[colframe=white,colback=white]\begin{equation}" + match + r"\end{equation}\end{tcolorbox}" + suffix
    elif mode == 1:
        return prefix + r"\begin{tcolorbox}[colframe=white,colback=black]\begin{equation}" + match + r"\end{equation}\end{tcolorbox}" + suffix

def regenerate_latex(texfile, NEWDIR):
    os.makedirs(NEWDIR, exist_ok=True)
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
    highlight_formulas_filename = osp.join(NEWDIR, highlight_formulas_filename + NEW_LATEX_FILE_SUFFIX)

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

# test
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True, help="file path to the latex file")
    parser.add_argument("-d", "--destination", required=True, help="path to the destination directory")
    args = parser.parse_args()

    regenerate_latex(args.source, args.destination, mode=1)