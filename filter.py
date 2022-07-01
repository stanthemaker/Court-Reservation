from PIL import Image
import cv2 as cv
import numpy as np

# import pytesseract
# from matplotlib import pyplot as plt


def filterImage(img):
    # img = cv.imread(path)
    print(type(img))
    I_height, I_width = img.size
    image = np.asarray(img)
    for i in range(I_width):
        for j in range(I_height):
            if ((int(image[i, j, 0]) - int(image[i, j, 1])) < 10) or (
                int(image[i, j, 0]) - int(image[i, j, 2]) < 10
            ):
                image[i, j, 0] = 255
                image[i, j, 1] = 255
                image[i, j, 2] = 255
    img = Image.fromarray(image)

    result = cv.cvtColor(np.asarray(img), cv.COLOR_BGR2RGB)
    # result = np.asarray(img)[:,:,:3]
    height, width, _ = result.shape
    white = [255, 255, 255]
    black = [0, 0, 0]
    for i in range(width):
        for j in range(height):
            if i == 0 or j == 0 or i == width - 1 or j == height - 1:
                result[j, i] = white
            elif (
                (result[j - 1, i] == white).all() and (result[j + 1, i] == white).all()
            ) or (
                (result[j, i - 1] == white).all() and (result[j, i + 1] == white).all()
            ):
                # if i >= 3 and i <= width - 4:
                try:
                    if (result[j, i] == result[j, i + 3]).all() and (
                        result[j, i] == result[j, i - 3]
                    ).all():
                        pass
                    else:
                        result[j, i] = white
                except IndexError:
                    result[j, i] = white
                    continue
    for i in range(width):
        for j in range(height):
            if i != 0 and i != width - 1 and j != 0 and j != height - 1:
                if (
                    (result[j - 1, i] == white).all()
                    and (result[j + 1, i] == white).all()
                ) and (
                    (result[j, i - 1] == white).all()
                    and (result[j, i + 1] == white).all()
                ):
                    result[j, i] = white
    final = result.copy()

    gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    retval, binary = cv.threshold(gray, 250, 255, cv.THRESH_BINARY)
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            if (
                (result[j, i] == black).all()
                and (result[j, i + 1] == white).all()
                and (result[j, i - 1] == white).all()
            ):
                result[j, i - 1] = black
                result[j, i + 1] = black
            if (
                (result[j, i] == black).all()
                and (result[j + 1, i] == white).all()
                and (result[j - 1, i] == white).all()
            ):
                result[j - 1, i] = black
                result[j + 1, i] = black
    final = cv.medianBlur(binary, 1)
    source = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    final = cv.medianBlur(source, 1)
    # cv.imwrite("./filtered.png", final)

    final = Image.fromarray(final)
    return final


# validation
# ans = open('./imgs/ans', 'r')
# total = 0
# correct = 0
# fully_correct = []
# almost_correct = []
# for num in range(100):
#     img = Image.open('./filtered/{}.png'.format(num))
#     text = pytesseract.image_to_string(img, lang='eng')
#     total += 4
#     line = ans.readline()
#     tmp = 0
#     for ch, pred in zip(line, text):
#         if ch == '\n':
#             break
#         elif ch == pred:
#             correct += 1
#             tmp += 1
#     if tmp == 4:
#         fully_correct.append(num)
#     elif tmp == 3:
#         almost_correct.append(num)
#     # print("img{}, text: {}".format(num, text))
# print("total: {}, correct: {}".format(total, correct))
# print("fully correct: {}".format(fully_correct))
# print("accuracy:{}, pass number: {}/100, with one digit wrong: {}".format(correct/total, len(fully_correct), len(almost_correct)))


# plot image
# images = [img, final]
# titles = ['Source Image', 'Color Image']
# for i in range(2):
#     plt.subplot(1, 2, i + 1), plt.imshow(images[i], 'gray')
#     plt.title(titles[i])
#     plt.xticks([]), plt.yticks([])

# plt.show()
