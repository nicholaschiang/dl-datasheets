#! /usr/bin/env python

# NOTE: Using this script becuase Acrobat is terrible software and doesn't
# actually do the batch files in order, and crashes. This is used to move the
# PDFs that have corresponding HTMLS out of the source folder so that I can see
# which PDFs still need to be converted.

import os
import shutil
import random
# html_src = "/home/lwhsiao/Desktop/data/digikey_train_html/"
# src = "/home/lwhsiao/Desktop/data/digikey_train_pdf/"
# dest = "/home/lwhsiao/Desktop/data/digikey_train_html_new/"

def choose_random_files(num_files, dont_copy=False):
    """
    Get num_files random indices into the directory and copy the HTML and PDF over.
    """
    selected_files = set()
    pdf_src = "/home/lwhsiao/Desktop/data/test_pdf/"
    html_src = "/home/lwhsiao/Desktop/data/test_html/"
    pdf_dest = "/home/lwhsiao/Desktop/data/dev_pdf/"
    html_dest = "/home/lwhsiao/Desktop/data/dev_html/"
    src_files = os.listdir(pdf_src)
    random_indices = []
    while len(set(random_indices)) != num_files:
        random_indices = [random.randint(0, len(src_files)-1) for _ in range(num_files)]

    # print random_indices;
    # print len(set(random_indices))

    for i in random_indices:
        file_name = src_files[i]
        html_filename = file_name[:-3] + "html"
        pdf_filename = file_name
        full_html_filename = os.path.join(html_src, html_filename)
        full_pdf_filename = os.path.join(pdf_src, pdf_filename)

        if (os.path.isfile(full_html_filename) and os.path.isfile(full_pdf_filename)):
            selected_files.add((full_pdf_filename, full_html_filename))

        else:
            print "[error] " + full_pdf_filename

    summary_sheets = set(['/home/lwhsiao/Desktop/data/test_pdf/CentralSemiconductorCorp_2N4013.pdf',
                    '/home/lwhsiao/Desktop/data/test_pdf/CentralSemiconductorCorp_TIP147.pdf',
                    '/home/lwhsiao/Desktop/data/test_pdf/CentralSemiconductorCorp_2N3416.pdf'])

    if len(summary_sheets.intersection(set([pdf for pdf, html in selected_files]))) == 1:
        print "One overlap."
        for full_pdf_filename, full_html_filename in sorted(selected_files):
            print full_pdf_filename
            if not dont_copy:
                shutil.move(full_pdf_filename, pdf_dest)
                shutil.move(full_html_filename, html_dest)

choose_random_files(25, dont_copy=False)

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
