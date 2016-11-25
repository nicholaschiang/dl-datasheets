#! /usr/bin/env python

# NOTE: Using this script becuase Acrobat is terrible software and doesn't
# actually do the batch files in order, and crashes. This is used to move the
# PDFs that have corresponding HTMLS out of the source folder so that I can see
# which PDFs still need to be converted.

import os
import shutil

src = "/home/lwhsiao/Desktop/clean_html/"
pdf_src = "/home/lwhsiao/Desktop/transistor_pdfs/"
dest = "/home/lwhsiao/Desktop/clean_pdfs/"

src_files = os.listdir(src)
for file_name in src_files:
    pdf_filename = file_name[:-4] + "pdf"
    # print pdf_filename
    full_file_name = os.path.join(pdf_src, pdf_filename)
    if (os.path.isfile(full_file_name)):
        shutil.move(full_file_name, dest)
    else:
        print "[error] " + full_file_name
