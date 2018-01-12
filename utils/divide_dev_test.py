#! /usr/bin/env python

import sys
import argparse
import os
import shutil
import random
import time

# TODO: This is all off the assumption that there is the same number of sanitized
#   PDFs and HTMLs. We are also assuming that filenames are the same, just different
#   extentions.

def parse_args():
    """
    Parse the arguments for the directory to read from and save to.
    """
    # Define what commandline arguments can be accepted
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir",metavar="PDF_DIRECTORY", type=check_str_is_dir,
                        help="Source directory containing PDF files")
    parser.add_argument("html_dir",metavar="HTML_DIRECTORY", type=check_str_is_dir,
                        help="Source directory containing HTML files")
    parser.add_argument('--test', dest="num_test", metavar="NUM_TEST", type=int, default=0, help="# documents in test set")
    parser.add_argument('--dev', dest="num_dev", metavar="NUM_DEV", type=int, default=0, help="# of documents in dev set")
    parser.add_argument('--sim', dest="simulate", action='store_true', default=False, help="Just print what would be moved, don't actually move")
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.0')
    args = vars(parser.parse_args())

    return args

def check_str_is_dir(input_path):
    directory = input_path
    # Check that string has trailing slash
    if not directory.endswith('/'):
         directory + '/'

    # Check for destination directory
    if not os.path.exists(directory):
        raise argparse.ArgumentTypeError("This directory does not exist. Please create it first.")

    return directory

def choose_random_files(num_test, num_dev, pdf_dir, html_dir, dont_copy=False):
    """
    Get num_files random indices into the directory and copy the HTML and PDF over.
    """
    base_directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'dataset'))
    test_pdf_dest = os.path.join(base_directory, "test/pdf/")
    test_html_dest = os.path.join(base_directory, "test/html/")
    dev_pdf_dest = os.path.join(base_directory, "dev/pdf/")
    dev_html_dest = os.path.join(base_directory, "dev/html/")
    train_pdf_dest = os.path.join(base_directory, "train/pdf/")
    train_html_dest = os.path.join(base_directory, "train/html/")

    directories = [ test_pdf_dest, test_html_dest,
                    dev_pdf_dest, dev_html_dest,
                    train_html_dest, train_pdf_dest]

    # Create the test and dev folders in the directory where this script is run
    for directory in directories:
        if not os.path.exists(directory) and not dont_copy:
            os.makedirs(directory)

    pdf_src_files = sorted(os.listdir(pdf_dir))
    html_src_files = sorted(os.listdir(html_dir))

    # Randomly shuffle indexes, then use this list to create each set. Note
    # that these are based on HTML files, rather than the PDF files since some
    # PDFs fail to convert correctly. We want to pull the original, unsanitized
    # PDFs that converted correctly.
    random_indices = range(0, len(html_src_files))
    random.shuffle(random_indices)

    # First pull out test
    for i in range(0, len(html_src_files)):
        file_name = html_src_files[random_indices[i]]
        pdf_filename = file_name[:-4] + "pdf"
        html_filename = file_name
        full_html_filename = os.path.join(html_dir, html_filename)
        full_pdf_filename = os.path.join(pdf_dir, pdf_filename)

        # NOTE: this code also expects that all filenames are lowercased and
        # deduplicated so that acrobat doesn't add the '_1' to different capitalizations

        if i < num_test: # place in Test set
            if (os.path.isfile(full_html_filename) and os.path.isfile(full_pdf_filename)):
                print("[test]   " + str(i) + ": " + test_pdf_dest + pdf_filename)
                if not dont_copy:
                    shutil.copy(full_pdf_filename, test_pdf_dest)
                    shutil.copy(full_html_filename, test_html_dest)
            else:
                print "[error] %s and %s" % (full_pdf_filename, full_html_filename)


        elif i < (num_test + num_dev): # place in Dev set
            if (os.path.isfile(full_html_filename) and os.path.isfile(full_pdf_filename)):
                print("[dev]   " + str(i) + ": " + dev_pdf_dest + pdf_filename)
                if not dont_copy:
                    shutil.copy(full_pdf_filename, dev_pdf_dest)
                    shutil.copy(full_html_filename, dev_html_dest)
            else:
                print "[error] %s and %s" % (full_pdf_filename, full_html_filename)

        else: # rest is training data
            if (os.path.isfile(full_html_filename) and os.path.isfile(full_pdf_filename)):
                print("[train]   " + str(i) + ": " + train_pdf_dest + pdf_filename)
                if not dont_copy:
                    shutil.copy(full_pdf_filename, train_pdf_dest)
                    shutil.copy(full_html_filename, train_html_dest)
            else:
                print "[error] %s and %s" % (full_pdf_filename, full_html_filename)


# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    args = parse_args()
    start_time = time.time()
    num_test = args["num_test"]
    num_dev = args["num_dev"]
    print('Creating %d test and %d dev sets.' % (num_test, num_dev))

    choose_random_files(num_test, num_dev, args["pdf_dir"], args["html_dir"], args["simulate"])

    finish_time = time.time()
    print('Took ' + str(finish_time - start_time) + ' sec total.')
