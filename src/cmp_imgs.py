# import the necessary packages
from skimage.metrics import structural_similarity as compare_ssim
import argparse
import imutils
import cv2
import numpy as np

AREA_THRESHOLD = 600

"""
cmp_imgs(imageA_path,imageB_path)
    功能：比较两张图片是否一样，如果不一样，返回不一样的区域的bounding box
    输入：两张图片的路径
    输出：不一样的区域的bounding box
    例子：
        bboxes = compare_image("workspace/tmp/Original.jpg","workspace/tmp/Modified.jpg")
        print(bboxes)
        # 输出：[(0, 0, 640, 480)]
"""

def cmp_imgs(imageA_path,imageB_path):
    # load the two input images
    imageA = cv2.imread(imageA_path)
    imageB = cv2.imread(imageB_path)

    # 先判断两张图片是否一致
    difference = cv2.subtract(imageA, imageB)
    result = not np.any(difference) #if difference is all zeros it will return False
    
    if result is True:
        print ("两张图片一样")
        return None
    else:
        print ("两张图片不一样")

    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    # print("SSIM: {}".format(score)) # debug

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    bboxes = [cv2.boundingRect(c) for c in cnts]

    # drop the bbox with small area, which is probably noise
    bboxes = [bbox for bbox in bboxes if bbox[2]*bbox[3] > AREA_THRESHOLD]

    # # loop over the contours
    # for c in cnts:
    #     # compute the bounding box of the contour and then draw the
    #     # bounding box on both input images to represent where the two
    #     # images differ
    #     (x, y, w, h) = cv2.boundingRect(c)
    #     print(x, y, w, h)
    #     # the next is to paint the bounding box on the image
    #     # cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #     # cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # show the output images 这个是打开图片，这里不需要
    #cv2.imshow("Original", imageA)
    #cv2.imshow("Modified", imageB)
    #cv2.imshow("Diff", diff)
    #cv2.imshow("Thresh", thresh)

    # 保存图片
    cv2.imwrite("workspace/tmp/Original.jpg",imageA)
    cv2.imwrite("workspace/tmp/Modified.jpg",imageB)
    cv2.imwrite("workspace/tmp/thresh.jpg",thresh)
    cv2.imwrite("workspace/tmp/diff.jpg",diff)

    # cv2.destroyAllWindows()

    #cv2.waitKey(0)
    return bboxes

if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--first", required=True,
        help="first input image")
    ap.add_argument("-s", "--second", required=True,
        help="second input image")
    args = vars(ap.parse_args())
    bboxes = cmp_imgs(args["first"],args["second"])
    print(bboxes)