# import the necessary packages
from skimage.metrics import structural_similarity as compare_ssim
import argparse
import imutils
import cv2
import numpy as np

# WIDTH_SCALE = 1.05
# HEIGHT_SCALE = 1.5

# def adjust_bbox(bbox, width_scale, height_scale):
#     """
#     功能：根据比例调整 bbox 大小
#     输入：bbox (x, y, w, h) - 原始 bbox 坐标和大小
#          width_scale - 宽度调整比例，例如 0.8 表示缩小到原来宽度的 80%，1.2 表示放大到原来宽度的 120%
#          height_scale - 高度调整比例，例如 0.8 表示缩小到原来高度的 80%，1.2 表示放大到原来高度的 120%
#     输出：调整后的 bbox 坐标和大小
#     """
#     x, y, w, h = bbox
#     new_w = int(w * width_scale)
#     new_h = int(h * height_scale)
#     new_x = x + (w - new_w) // 2
#     new_y = y + (h - new_h) // 2
#     return (new_x, new_y, new_w, new_h)

WIDTH_SCALE = 0.01
HEIGHT_SCALE = 0.01

def adjust_bbox(bbox, img_height, img_width, height_scale, width_scale):
    x, y, w, h = bbox
    new_w = img_width * width_scale + w
    new_h = img_height * height_scale + h
    new_x = x - (new_w - w) // 2
    new_y = y - (new_h - h) // 2
    return (new_x, new_y, new_w, new_h)

def find_elements(array, target_value):
    indices = np.where(np.all(array == target_value, axis=-1))
    indices_2d = np.column_stack((indices[0], indices[1]))
    # --------------------------------------------------------
    # for idx in indices_2d:
    #     print(idx)
    # print(len(indices_2d))
    # print(indices_2d.shape)
    # --------------------------------------------------------
    # 使用 np.unique 按第一维的数值进行归类计数
    unique_values, counts = np.unique(indices_2d[:, 0], return_counts=True)
    sorted(unique_values)
    if len(unique_values) == 0:
        return None
    yoff_min = unique_values[0]
    yoff_max = unique_values[-1]

    # --------------------------------------------------------
    # 打印结果
    # for value, count in zip(unique_values, counts):
        # print(f"第一维值为 {value} 的元素出现了 {count} 次")
    # --------------------------------------------------------

    # 使用 np.unique 按第二维的数值进行归类计数
    unique_values, counts = np.unique(indices_2d[:, 1], return_counts=True)
    sorted(unique_values)
    xoff_min = unique_values[0]
    xoff_max = unique_values[-1]

    # --------------------------------------------------------
    # 打印结果
    # for value, count in zip(unique_values, counts):
        # print(f"第二维值为 {value} 的元素出现了 {count} 次")
    # --------------------------------------------------------

    return xoff_min, yoff_min, xoff_max, yoff_max

# 按最后一个维度聚类
def group_by_last_dim(array):
    # 使用 np.unique 按最后一个维度的值进行归类计数
    flattened_data = array.reshape(-1, 3)  # 将最后一个维度展平为二维数组
    unique_values, counts = np.unique(flattened_data, axis=0, return_counts=True)

    # --------------------------------------------------------
    # 打印结果
    for value, count in zip(unique_values, counts):
        print(f"值为 {value} 的元素出现了 {count} 次")
    # --------------------------------------------------------

def crop_bbox(img_path, bbox_list):
    """
    crop_bbox(img_path, bbox_list)
    input:
        img_path: the path of the image
        bbox_list: the list of bbox in the form of (x,y,w,h)
    output:
        new_bbox_list: the list of new bbox in the form of (x,y,w,h)
    """
    if bbox_list is None or len(bbox_list) == 0:
        return None
    new_bbox_list = []
    img = cv2.imread(img_path)
    img_height = img.shape[0]
    img_width = img.shape[1]
    for bbox in bbox_list:
        x,y,w,h = bbox
        crop_img = img[y:y+h, x:x+w]
        # print the shape and others
        # print(crop_img)
        # print(crop_img.shape)
        # print(crop_img.size)
        # print(crop_img.dtype)
        # find the pixel equal to the color of the equation and store the index in 2D array
        find_off = find_elements(crop_img, [0, 0, 0])
        if find_off is None:
            continue
        else:
            xoff_min, yoff_min, xoff_max, yoff_max = find_off
        # group_by_last_dim(crop_img) 
        # store the new bbox in the form of (x,y,w,h)
        new_x, new_y, new_w, new_h = x+xoff_min, y+yoff_min, xoff_max-xoff_min, yoff_max-yoff_min
        new_x, new_y, new_w, new_h = adjust_bbox((new_x, new_y, new_w, new_h), img_height=img_height, img_width=img_width, width_scale=WIDTH_SCALE, height_scale=HEIGHT_SCALE)
        new_bbox_list.append([new_x, new_y, new_w, new_h])

    return new_bbox_list

def show_bbox(img_path, bbox_list, save_path=None):
    """
    show_bbox(img_path, bbox_list)
    input:
        img_path: the path of the image
        bbox_list: the list of bbox in the form of (x,y,w,h)
    output:
        None
    """
    img = cv2.imread(img_path)
    if bbox_list is None or len(bbox_list) == 0:
        pass
    else:
        for bbox in bbox_list:
            x,y,w,h = bbox
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    # if not identify the save_path, save the new image in the same path but a little different(a.jpg -> a.new.jpg), otherwise save the image in the save_path
    if save_path is None:
        cv2.imwrite(img_path[:-4]+".new"+img_path[-4:], img)
    else:
        cv2.imwrite(save_path, img)

if __name__ == "__main__":
    # read the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="path to the input image")
    # read the list of bboxes
    parser.add_argument("-b", "--bbox", nargs='+', type=str, required=True, help="the list of bbox in the form of x,y,w,h, and the bbox is separated by space")
    parser.add_argument("-s", "--save", required=False, help="path to the save image")
    parser.add_argument("-show", "--show", action="store_true", help="enable show the image")
    args = vars(parser.parse_args())
    ori_bbox = [tuple(map(int, arg.split(','))) for arg in args["bbox"]]
    af_crop_bbox = crop_bbox(args["image"], ori_bbox)
    print(f"crop_bbox: {af_crop_bbox}")
    if args["show"]:
        show_bbox(args["image"], af_crop_bbox, args["save"])