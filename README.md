# ERC OCR
ERC OCR is a Python program that scans a snapshot of a Vietnamese enterprise registration certificate (can work on other language with minor modification) and outputs its data in a json file.

## Setup
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries.
```bash
pip install -r requirements.txt
```

## Usage
Initialize the server through the app.py file.
```bash
python app.py
```
Access localhost:5000 in browser.
Upload the file and press the Scan button. The json file will be exported to the output directory.