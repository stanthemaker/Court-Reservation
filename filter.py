import cv2
import numpy as np
import os
from PIL import Image

def filterImage(img): #type img = PIL.image
    cv_img= cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2RGB) 
    mask_1 = ((cv_img[:, :, 2] - cv_img[:, :, 1]) > 40) * ((cv_img[:, :, 2] - cv_img[:, :, 0]) > 40)
    mask_2 = np.sum(cv_img, axis=-1) < 475

    mask = mask_1 * mask_2
    cv_img[:, :, 0] *= mask
    cv_img[:, :, 1] *= mask
    cv_img[:, :, 2] *= mask
    PIL_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    return PIL_img
    # save_path = os.path.join("processed", file)
    # cv2.imwrite(save_path, cv_img)


# if __name__ == "__main__":
#     files = [f for f in os.listdir("Screenshots") if ".png" in f]
#     files.sort()
#     if not os.path.exists("processed"):
#         os.mkdir("processed")

#     for file in files:
#         cv_img_path = os.path.join("Screenshots", file)
#         cv_cv_img= cv2.imread(cv_img_path, cv2.IMREAD_COLOR)
#         # kernel = np.ones((3, 3), np.uint8)
#         # cv_cv_img= cv2.erode(cv_img, kernel, iterations=1)
#         mask_1 = ((cv_img[:, :, 2] - cv_img[:, :, 1]) > 40) * ((cv_img[:, :, 2] - cv_img[:, :, 0]) > 40)
#         mask_2 = np.sum(cv_img, axis=-1) < 475

#         mask = mask_1 * mask_2
#         cv_img[:, :, 0] *= mask
#         cv_img[:, :, 1] *= mask
#         cv_img[:, :, 2] *= mask
#         kernel = np.ones((3, 3), np.uint8)
#         save_path = os.path.join("processed", file)
#         cv2.imwrite(save_path, cv_img)
