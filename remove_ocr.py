# Removes the PDF/HTML pair of documents that need OCR.

import subprocess
import os

train_digikey_html = "/home/lwhsiao/Desktop/data/digikey_train_html/"
train_digikey_pdf = "/home/lwhsiao/Desktop/data/digikey_train_pdf/"
train_other_html = "/home/lwhsiao/Desktop/data/other_train_html/"
train_other_pdf = "/home/lwhsiao/Desktop/data/other_train_pdf/"
dev_pdf = "/home/lwhsiao/Desktop/data/dev_pdf/"
dev_html = "/home/lwhsiao/Desktop/data/dev_html/"

directories = [(dev_pdf, dev_html), (train_digikey_pdf, train_digikey_html), (train_other_pdf, train_other_html)]

# output = subprocess.Popen(["pdffonts", "/home/lwhsiao/Desktop/data/workspace/2SC2482-Toshiba-datasheet-101457.pdf"], stdout=subprocess.PIPE).communicate()[0]
output = subprocess.Popen(["pdffonts", "/home/lwhsiao/Desktop/data/workspace/2SC3503-Sanyo-datasheet-101941.pdf"], stdout=subprocess.PIPE).communicate()[0]

log = open("removed_files.txt", "w")

for pdf_directory, html_directory in directories:
    src_files = os.listdir(pdf_directory)
    for pdf in src_files:
        if (pdf == ".DS_Store"):
            continue

        pdf_filename = os.path.join(pdf_directory, pdf)
        html_filename = os.path.join(html_directory, pdf[:-3] + "html")
        # print pdf_filename
        if (os.path.isfile(pdf_filename)):
            output = subprocess.Popen(["pdffonts", pdf_filename], stdout=subprocess.PIPE).communicate()[0]
            if (len(output.split('\n')) <= 3):
                # this has no fonts and thus is an image.
                log.write(pdf_filename + ", " + html_filename + '\n')
                print pdf_filename + ", " + html_filename
                os.remove(pdf_filename)
                os.remove(html_filename)

log.close()
