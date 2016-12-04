#! /usr/bin/env python

# NOTE: Using this script becuase Acrobat is terrible software and doesn't
# actually do the batch files in order, and crashes. This is used to move the
# PDFs that have corresponding HTMLS out of the source folder so that I can see
# which PDFs still need to be converted.

import os
import shutil
import random
html_src = "/home/lwhsiao/Desktop/data/digikey_train_html/"
src = "/home/lwhsiao/Desktop/data/digikey_train_pdf/"
dest = "/home/lwhsiao/Desktop/data/digikey_train_html_new/"

def choose_100_random_files():
    """
    Get 100 random indices into the directory and copy the HTML and PDF over.
    """
    pdf_src = "/home/lwhsiao/Desktop/data/digikey_train_pdf/"
    html_src = "/home/lwhsiao/Desktop/data/digikey_train_html/"
    pdf_dest = "/home/lwhsiao/Desktop/data/test_pdf/"
    html_dest = "/home/lwhsiao/Desktop/data/test_html/"
    src_files = os.listdir(pdf_src)
    random_indices = []
    while len(set(random_indices)) != 100:
        random_indices = [random.randint(0, len(src_files)) for _ in range(100)]

    print random_indices;
    print len(set(random_indices))

    for i in random_indices:
        file_name = src_files[i]
        html_filename = file_name[:-3] + "html"
        pdf_filename = file_name
        full_html_filename = os.path.join(html_src, html_filename)
        full_pdf_filename = os.path.join(pdf_src, pdf_filename)

        if (os.path.isfile(full_html_filename) and os.path.isfile(full_pdf_filename)):
            shutil.move(full_pdf_filename, pdf_dest)
            shutil.move(full_html_filename, html_dest)
            # print full_pdf_filename
        else:
            print "[error] " + full_pdf_filename


choose_100_random_files()

# # NOTE: Use this to copy pdfs corresponding to src htmls.
# src = "/home/lwhsiao/Desktop/digikey-remaining-html/"
# pdf_src = "/home/lwhsiao/Desktop/transistors/digikey-singlebjts-pdf/"
# dest = "/home/lwhsiao/Desktop/digikey-singlebjts-pdf/"
#
# src_files = os.listdir(src)
# for file_name in src_files:
#     pdf_filename = file_name[:-4] + "pdf"
#     # print pdf_filename
#     full_file_name = os.path.join(pdf_src, pdf_filename)
#     if (os.path.isfile(full_file_name)):
#         shutil.move(full_file_name, dest)
#     else:
#         print "[error] " + full_file_name
