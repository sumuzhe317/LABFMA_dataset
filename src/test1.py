import re

# 正则表达式
# pattern = r"\n(\\begin\{equation\})(.*?)(\\end\{equation\})|\n(\\\[)(.*?)(\\\])"
LONG_MATH_PATTERNS = r"\n\\begin\{equation\}.*?\\end\{equation\}|\n\$\$.*?\$\$|\n\\\[.*?\\\]|\n\\\(.*?\\\)|\n\\begin\{multline\}.*?\\end\{multline\}|\n\\begin\{gather\}.*?\\end\{gather\}|\n\\begin\{align\}.*?\\end\{align\}|\n\\begin\{alignat\}.*?\\end\{alignat\}|\n\\begin\{flalign\}.*?\\end\{flalign\}|\n\\begin\{equation\*\}.*?\\end\{equation\*\}|\n\\begin\{multline\*\}.*?\\end\{multline\*\}|\n\\begin\{gather\*\}.*?\\end\{gather\*\}|\n\\begin\{align\*\}.*?\\end\{align\*\}|\n\\begin\{alignat\*\}.*?\\end\{alignat\*\}|\n\\begin\{flalign\*\}.*?\\end\{flalign\*\}"

REPROCESS_MATH_PATTERNS = r"\n(\\begin\{equation\}|\$\$|\\\[|\\\(|\\begin\{multline\}|\\begin\{gather\}|\\begin\{align\}|\\begin\{alignat\}|\\begin\{flalign\}|\\begin\{equation\*\}|\\begin\{multline\*\}|\\begin\{gather\*\}|\\begin\{align\*\}|\\begin\{alignat\*\}|\\begin\{flalign\*\})(.*?)(\\end\{equation\}|\$\$|\\\]|\\\)|\\end\{multline\}|\\end\{gather\}|\\end\{align\}|\\end\{alignat\}|\\end\{flalign\}|\\end\{equation\*\}|\\end\{multline\*\}|\\end\{gather\*\}|\\end\{align\*\}|\\end\{alignat\*\}|\\end\{flalign\*\})"
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
# 用法示例：
test_string = r"""
Some text before the equation.

\begin{equation}
    E = mc^2
\end{equation}

Some text after the equation.

$$
    \sum_{i=1}^{n} x_i
$$

\[
    a^2 + b^2 = c^2
\]

\begin{multline}
    a + b + c + \\
    d + e + f
\end{multline}

\begin{gather}
    x + y = z \\
    2x - 3y = 0
\end{gather}

\begin{align}
    x &= 2y \\
    3x + y &= 10
\end{align}

\begin{alignat}{2}
    x &= 2y & \quad & \text{First equation} \\
    3x + y &= 10 & \quad & \text{Second equation}
\end{alignat}

\begin{flalign}
    x &= 2y \\
    3x + y &= 10
\end{flalign}

Some text before the equation.

\begin{equation}
    E = mc^2
\end{equation}

Some text after the equation.

\begin{equation*}
    a^2 + b^2 = c^2
\end{equation*}

\begin{equation*}
    x = y + z
\end{equation*}

\begin{multline*}
    a + b + c + \\
    d + e + f
\end{multline*}

\begin{multline*}
    x = y + z \\
    a = b + c
\end{multline*}

\begin{gather*}
    x + y = z \\
    2x - 3y = 0
\end{gather*}

\begin{gather*}
    a = b + c \\
    x = y + z
\end{gather*}

\begin{align*}
    x &= 2y \\
    3x + y &= 10
\end{align*}

\begin{align*}
    a &= b + c \\
    x &= y + z
\end{align*}

\begin{alignat*}{2}
    x &= 2y & \quad & \text{First equation} \\
    3x + y &= 10 & \quad & \text{Second equation}
\end{alignat*}

\begin{alignat*}{2}
    a &= b + c & \quad & \text{Equation 1} \\
    x &= y + z & \quad & \text{Equation 2}
\end{alignat*}

\begin{flalign*}
    x &= 2y \\
    3x + y &= 10
\end{flalign*}

\begin{flalign*}
    a &= b + c \\
    x &= y + z
\end{flalign*}

"""

for match in re.finditer(LONG_MATH_PATTERNS, test_string, re.DOTALL):
    print('Found equation:','-'*50)
    print('original:', match.group(0))
    match = re.search(REPROCESS_MATH_PATTERNS, match.group(0), re.DOTALL)
    print('reprocess:', match.group(0))
    print('prefix', match.group(1))
    print('content', match.group(2))
    print('suffix', match.group(3))