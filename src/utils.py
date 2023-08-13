import os
import shutil


def remove_substring(original_string, substring_to_remove):
    new_string = original_string.replace(substring_to_remove, '')
    return new_string

def remove_temp_files(directory_path):
    files = os.listdir(directory_path)
    for file_name in files:
        if not file_name.endswith(".tex"):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

def remove_folder(folder_path):
    if os.path.exists(folder_path):
        os.system("rm -rf " + folder_path)

# # 使用示例
# folder_path = '/mnt/sda/2022-0526/home/scc/zty/workspace/doc-seg/dataset/LABFMA_dataset/texfile'
# add_tex_extension_to_files(folder_path)
def add_tex_extension_to_files(folder_path):
    """
    遍历指定文件夹下的所有文件，为没有后缀的文件添加'.tex'后缀。

    参数:
    folder_path (str): 文件夹路径
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file)

            # 如果文件没有后缀，则添加'.tex'后缀
            if not file_extension:
                new_file_path = file_path + '.tex'
                os.rename(file_path, new_file_path)
                print(f"Renamed {file} to {filename}.tex")


# # 使用示例
# folder_path = "/mnt/sda/2022-0526/home/scc/zty/workspace/doc-seg/dataset/LABFMA_dataset/texfile/test"
# check_regex_in_files(folder_path)
def check_regex_in_files(folder_path):
    """
    遍历指定文件夹下的所有文件，检查是否包含给定的正则表达式。

    参数:
    folder_path (str): 文件夹路径。

    返回:
    None (如果正则表达式在某个文件中不存在，则打印错误信息并退出程序)。
    """
    docclass_regex = r'^\\documentclass.*$'
    docstyle_regex = r'^\\documentstyle.*$'
    usepackage_regex = r'^\\usepackage.*$'
    title_regex = r'^\\Title.*$'

    # 获取指定文件夹下所有文件的排序列表
    files = sorted([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    # 设置一个bool数组，用于记录每个文件是否包含给定的正则表达式
    files_contain_regex = [False] * len(files)

    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            print(f"Checking file: {file}", "-" * 28)
            content = f.read()
            docclass_match = re.search(docclass_regex, content, re.MULTILINE)
            usepackage_match = re.search(usepackage_regex, content, re.MULTILINE)
            docstyle_match = re.search(docstyle_regex, content, re.MULTILINE)
            title_match = re.search(title_regex, content, re.MULTILINE)

            if docclass_match:
                print(f"File: {file}, \\documentclass found at position {docclass_match.start()}")
                print(f"File: {file}, \\documentclass found in context {docclass_match.group(0)}")
                files_contain_regex[files.index(file)] = True
            else:
                print(f"Error: File {file} does not contain \\documentclass")
                # return

            if docstyle_match:
                print(f"File: {file}, \\documentstyle found at position {docstyle_match.start()}")
                print(f"File: {file}, \\documentstyle found in context {docstyle_match.group(0)}")
                files_contain_regex[files.index(file)] = True
            else:
                print(f"Error: File {file} does not contain \\documentstyle")
                # return

            if usepackage_match:
                print(f"File: {file}, \\usepackage found at position {usepackage_match.start()}")
                print(f"File: {file}, \\usepackage found in context {usepackage_match.group(0)}")
                files_contain_regex[files.index(file)] = True
            else:
                print(f"Error: File {file} does not contain \\usepackage")
                # return
            
            if title_match:
                print(f"File: {file}, \\Title found at position {title_match.start()}")
                print(f"File: {file}, \\Title found in context {title_match.group(0)}")
                files_contain_regex[files.index(file)] = True
            else:
                print(f"Error: File {file} does not contain \\Title")
                # return
    
    # 找出 files_contain_regex 里为False的元素的索引
    false_indices = [i for i, x in enumerate(files_contain_regex) if not x]
    print(f"Files length: {len(files)}")
    print(f"false_indices length: {len(false_indices)}")
    print(f"Files that do not contain the regex: {false_indices}")
