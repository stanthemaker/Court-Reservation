import pytesseract

def filterImage(img): #type img = PIL.image
    cv_img= cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2RGB) 
    mask_1 = ((cv_img[:, :, 2] - cv_img[:, :, 1]) > 40) * ((cv_img[:, :, 2] - cv_img[:, :, 0]) > 40)
    mask_2 = np.sum(cv_img, axis=-1) < 475

    mask = mask_1 * mask_2
    cv_img[:, :, 0] *= mask
    cv_img[:, :, 1] *= mask
    cv_img[:, :, 2] *= mask
    filtered_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    return filtered_img

def recognition(self, im):
    img = self.filterImage(im)
    number = pytesseract.image_to_string(img)
    return number
