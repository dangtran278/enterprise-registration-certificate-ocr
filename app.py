import os, sys
cwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cwd + '\scan')
from scan import scan
sys.path.append(cwd + '\ocr')
from data_extractor import extract

import cv2, json

from flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    r = lambda i: i.buffer.read() if hasattr(i, "buffer") else i.read()
    w = lambda o, data: o.buffer.write(data) if hasattr(o, "buffer") else o.write(data)
    dic = {}

    if request.method == 'POST':
        file = request.files['file']

        scpath = file.filename[:-4] + '-scanned.jpg'
        with open(scpath, 'wb') as scfile:
            w(scfile, scan(r(file)))
        scfile.close()

        img = cv2.imread(scpath)
        dic = extract(img)
        with open('output/'+file.filename[:-4]+'.json', 'w', encoding='utf8') as json_file:
            json.dump(dic, json_file, ensure_ascii=False)
        json_file.close()
        os.remove(scpath)

    return render_template('index.html', edict=dic)


if __name__ == "__main__":
    app.run(debug=True)