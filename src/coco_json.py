import json
import os

import cv2

def save_to_coco_json(images, annotations, categories, output_file):
    """
    保存数据为COCO格式的JSON文件

    参数:
    images (list): 包含图像信息的列表
    annotations (list): 包含注释信息的列表
    categories (list): 包含类别信息的列表
    output_file (str): 输出的JSON文件名
    """

    # 构建COCO格式的数据
    coco_data = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    print(coco_data)

    # 保存数据为JSON文件
    with open(output_file, "w") as f:
        json.dump(coco_data, f)

def combine_coco_files(input_files, output_file):
    """
    整合多个COCO格式的JSON文件

    参数:
    input_files (list): 包含多个输入JSON文件名的列表
    output_file (str): 输出的合并后JSON文件名
    """
    combined_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    image_id_offset = 0
    annotation_id_offset = 0

    # 逐个读取输入的JSON文件，并整合数据
    for file in input_files:
        with open(file, "r") as f:
            data = json.load(f)

            # 调整图像ID和注释ID，并更新注释中的图像ID
            for image in data["images"]:
                image["id"] += image_id_offset

            for annotation in data["annotations"]:
                annotation["id"] += annotation_id_offset
                annotation["image_id"] += image_id_offset

            # 更新ID偏移量
            image_id_offset = data["images"][-1]["id"] + 1
            annotation_id_offset = data["annotations"][-1]["id"] + 1

            # 整合数据
            combined_data["images"].extend(data["images"])
            combined_data["annotations"].extend(data["annotations"])
            combined_data["categories"].extend(data["categories"])

    # 保存整合后的数据为JSON文件
    with open(output_file, "w") as f:
        json.dump(combined_data, f)

def convert_and_save_coco_format(image_path, bbox_list, category_list, category_meta_dict, save_json_file_path):
    """
    将图像和bbox信息保存为COCO格式的JSON文件

    参数:
    image_path (str): 图像文件路径
    bbox_list (list): 包含bbox信息的列表，每个bbox为 (x, y, width, height) 的形式
    category_list (list): 包含bbox对应类别的列表，元素为类别标签
    category_meta_dict (dict): 包含类别元信息的字典，用于构建categories数据
    save_json_file_path (str): 输出的COCO格式JSON文件路径
    """
    # 使用cv2读取图片获取宽度和高度
    img = cv2.imread(image_path)
    height, width = img.shape[:2]

    # 创建 images 数据
    image_name = os.path.basename(image_path)
    image_id = 1  # 假设一个图片只有一个bbox
    images_data = [{
        "height": height,
        "width": width,
        "id": image_id,
        "file_name": image_name,
    }]

    # 创建 categories 数据
    categories_data = []
    for category_label, category_id in category_meta_dict.items():
        categories_data.append({"id": category_id, "name": category_label})

    # 创建 annotations 数据
    annotations_data = []
    if bbox_list and category_list:
        for bbox, category_label in zip(bbox_list, category_list):
            x, y, width, height = bbox
            x, y, width, height = float(x), float(y), float(width), float(height)  # 将bbox数据转换为浮点数
            area = width * height  # 计算bbox的面积
            annotation_id = len(annotations_data) + 1
            category_id = category_meta_dict[category_label]
            annotation_data = {
                "iscrowd": 0,  # 这里假设所有的bbox都不是crowd
                "image_id": image_id,
                "bbox": [x, y, width, height],
                "segmentation": [],  # 这里假设所有的bbox都不是分割区域
                "category_id": category_id,
                "id": annotation_id,
                "area": area,
            }
            annotations_data.append(annotation_data)

    save_to_coco_json(images_data, annotations_data, categories_data, save_json_file_path)


# 示例用法
if __name__ == "__main__":
    # 假设有一些数据
    images = [{"id": 1, "file_name": "image1.jpg", "height": 480, "width": 640}]
    annotations = [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [100, 200, 50, 50]}]
    categories = [{"id": 1, "name": "cat"}]

    # 调用函数保存为COCO格式的JSON文件
    save_to_coco_json(images, annotations, categories, "output.json")
    input_files = ["file1.json", "file2.json", "file3.json"]
    output_file = "combined.json"

    # 调用函数整合多个COCO格式的JSON文件
    combine_coco_files(input_files, output_file)


    image_path = "path/to/image.jpg"
    bbox_list = [(100, 100, 50, 50), (200, 200, 60, 40)]
    category_list = ["cat", "dog"]
    category_meta_dict = {"cat": 1, "dog": 2}
    save_json_file_path = "output.json"

    convert_and_save_coco_format(image_path, bbox_list, category_list, category_meta_dict, save_json_file_path)