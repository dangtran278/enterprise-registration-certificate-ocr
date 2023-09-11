import os, sys
import pytesseract

scdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '\scan'
print(scdir)
sys.path.append(scdir)
from scan import scan


def preprocess(data):
    from processors import Preprocessor, ShadowRemover, OtsuThresholder

    preproc = Preprocessor(
        processors = [
            ShadowRemover(kernel_size=(7,7), strength=21, output_process=False),
            OtsuThresholder(output_process=False)
        ]
    )

    extracted = preproc(data)
    return extracted


def ocr(s_img):
    p_img = preprocess(s_img)
    return pytesseract.image_to_string(p_img, lang='vie')
