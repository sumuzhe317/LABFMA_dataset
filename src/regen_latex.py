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

# 废弃方案1
# REPROCESS_MATH_PATTERNS = r"(\\begin\{equation\}|\$\$|\\\[|\\\(|\\begin\{align\}|\\begin\{gather\}|\\begin\{multline\}|\\begin\{split\}|\\begin\{flalign\*\}|\\begin\{alignat\}\{\d+\}|\\begin\{gathered\})(.*?)(\\end\{equation\}|\$\$|\\\]|\\\)|\\end\{align\}|\\end\{gather\}|\\end\{multline\}|\\end\{split\}|\\end\{flalign\*\}|\\end\{alignat\}|\\end\{gathered\})"

# 方案2
LONG_MATH_PATTERNS = r"[^\\]\\begin\{equation\}.*?\\end\{equation\}|[^\\]\$\$.*?\$\$|[^\\]\\\[.*?\\\]|[^\\]\\\(.*?\\\)|[^\\]\\begin\{multline\}.*?\\end\{multline\}|[^\\]\\begin\{gather\}.*?\\end\{gather\}|[^\\]\\begin\{align\}.*?\\end\{align\}|[^\\]\\begin\{alignat\}.*?\\end\{alignat\}|[^\\]\\begin\{flalign\}.*?\\end\{flalign\}|[^\\]\\begin\{equation\*\}.*?\\end\{equation\*\}|[^\\]\\begin\{multline\*\}.*?\\end\{multline\*\}|[^\\]\\begin\{gather\*\}.*?\\end\{gather\*\}|[^\\]\\begin\{align\*\}.*?\\end\{align\*\}|[^\\]\\begin\{alignat\*\}.*?\\end\{alignat\*\}|[^\\]\\begin\{flalign\*\}.*?\\end\{flalign\*\}"

REPROCESS_MATH_PATTERNS = r"[^\\](\\begin\{equation\}|\$\$|\\\[|\\\(|\\begin\{multline\}|\\begin\{gather\}|\\begin\{align\}|\\begin\{alignat\}|\\begin\{flalign\}|\\begin\{equation\*\}|\\begin\{multline\*\}|\\begin\{gather\*\}|\\begin\{align\*\}|\\begin\{alignat\*\}|\\begin\{flalign\*\})(.*?)(\\end\{equation\}|\$\$|\\\]|\\\)|\\end\{multline\}|\\end\{gather\}|\\end\{align\}|\\end\{alignat\}|\\end\{flalign\}|\\end\{equation\*\}|\\end\{multline\*\}|\\end\{gather\*\}|\\end\{align\*\}|\\end\{alignat\*\}|\\end\{flalign\*\})"

# define the header of tex file
TEX_HEADER_PATTERS = r'^\\usepackage.*$'
docclass_regex = r'^\\documentclass.*$'
docstyle_regex = r'^\\documentstyle.*$'
usepackage_regex = r'^\\usepackage.*$'
# title_regex = r'^\\Title.*$'
LONG_HEADER_PATTERNS = r'^(\\documentclass|\\documentstyle|\\usepackage)(.*$)'

NEW_LATEX_FILE_SUFFIX = ".tex"

def match_reprocess(match):
    reprocess_match = re.search(REPROCESS_MATH_PATTERNS, match.group(0), re.DOTALL)
    return reprocess_match

def check_regex_in_str(content):
    header_match = re.search(LONG_HEADER_PATTERNS, content, re.MULTILINE)
    return header_match

def rewrite_documentstyle(match):
    documentstyle_match = re.search(docstyle_regex, match, re.MULTILINE)
    if documentstyle_match is None:
        return match
    else: # rewrite documentstyle* to documentclass*
        rewritestr = re.sub(r'documentstyle', 'documentclass', documentstyle_match.group(0))
        return match[:documentstyle_match.start()] + "\n" + rewritestr + "\n" + match[documentstyle_match.end():]

def rewrite_header(match):
    ##########################################################
    # 废弃方案1
    # # match the header of tex file
    # header_str = re.search(TEX_HEADER_PATTERS, match, re.MULTILINE)
    # # print(match)
    # print(header_str.start())
    # with open("texfile/myhighlight.txt", "r") as file:
    #     myhighlight = file.read()
    # return match[:header_str.end()] + "\n" + myhighlight + "\n" + match[header_str.end():]
    ##########################################################
    # 方案2
    # match the header of tex file
    match = rewrite_documentstyle(match)
    header_match = check_regex_in_str(match)
    if header_match is None:
        return match
    with open("texfile/myhighlight.txt", "r") as file:
        myhighlight = file.read()
    # if header_match.group(1) == r'\Title':
    #     return match[:header_match.start()] + "\n" + myhighlight + "\n" + match[header_match.start():]
    # else:
    #     return match[:header_match.end()] + "\n" + myhighlight + "\n" + match[header_match.end():]
    return match[:header_match.end()] + "\n" + myhighlight + "\n" + match[header_match.end():]

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
    # 废弃方案3
    # match = remove_substring(match, "\eqno")
    # if mode == 0:
    #     return r"\begin{tcolorbox}[colframe=white,colback=white]" + "\n" + r"\begin{equation}" + match + r"\end{equation}" + "\n" + r"\end{tcolorbox}"
    # elif mode == 1:
    #     return r"\begin{tcolorbox}[colframe=white,colback=black]" + "\n" + r"\begin{equation}" + match + r"\end{equation}" + "\n" + r"\end{tcolorbox}"
    # 方案4
    match = remove_substring(match, "\eqno")
    if mode == 0:
        return "\n" + r"\begin{tcolorbox}[colframe=white,colback=white]" + "\n" + prefix + match + suffix + "\n" + r"\end{tcolorbox}"
    elif mode == 1:
        return "\n" + r"\begin{tcolorbox}[colframe=white,colback=black]" + "\n" + prefix + match + suffix + "\n" + r"\end{tcolorbox}"

def regenerate_latex(texfile, NEWDIR, mode):
    os.makedirs(NEWDIR, exist_ok=True)
    # 读取源文件内容
    texfile = osp.realpath(texfile)
    with open(texfile, 'r', encoding='utf-8-sig', errors='replace') as file:
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
                new_file.write(rewrite_header(latex_content[last_end:start]))
            else:
                new_file.write(latex_content[last_end:start])
            last_end = match.end()
            match = match_reprocess(match)
            # print('match is ',match.group(0))
            # print('prefix is ',match.group(1))
            # print('suffix is ',match.group(3))
            # conti = input('continue?')
            new_file.write(rewrite_math_mode(match=match.group(2),prefix=match.group(1),suffix=match.group(3), mode=mode))

        new_file.write(latex_content[last_end:])

# test
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True, help="file path to the latex file")
    parser.add_argument("-d", "--destination", required=True, help="path to the destination directory")
    args = parser.parse_args()

    regenerate_latex(args.source, args.destination, mode=1)