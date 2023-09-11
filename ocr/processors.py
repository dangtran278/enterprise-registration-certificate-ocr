import cv2
import numpy as np


class Preprocessor:
    def __init__(self, processors):
        self._processors = processors

    def __call__(self, img):
        self._processed = img
        for processor in self._processors:
            self._processed = processor(self._processed)
        return self._processed


class ShadowRemover:
    def __init__(self, kernel_size=(7,7), strength=21, output_process=False):
        self.output_process = output_process
        self._kernel = np.ones(kernel_size, np.uint8)
        self._strength = strength

    def __call__(self, img):
        rgb_planes = cv2.split(img)

        result_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, self._kernel)
            bg_img = cv2.medianBlur(dilated_img, self._strength)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(norm_img)

        result = cv2.merge(result_planes)
        if self.output_process: cv2.imwrite('remsd.jpg', result)
        return result


class OtsuThresholder:
    def __init__(self, thresh1=0, thresh2=255, output_process=False):
        self.output_process = output_process
        self._thresh1 = thresh1
        self._thresh2 = thresh2

    def __call__(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        T_, result = cv2.threshold(img, self._thresh1, self._thresh2, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.output_process: cv2.imwrite('thresholded.jpg', result)
        return result