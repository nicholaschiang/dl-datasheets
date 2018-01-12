import argparse
import os

from scraper_logging import debug_print
from scraper_logging import debug_print_warn
from scraper_logging import debug_print_error

class Flags(object):
    """ Holder object to contain dictionary key strings for the scurl flags"""
    CSV_DIR = "csv_dir"
    PDF_DIR = "pdf_dir"
    CSV_PAGES = "csv_pages"
    FV_CODE = "fv_code"
    KEEP_ENCRYPTED = "keep_encrypted"
    KEEP_OCR = "keep_ocr"
    KEEP_DUPLICATES = "keep_duplicates"
    SKIP_CSV_DL = "skip_csv_dl"
    SKIP_PDF_DL = "skip_pdf_dl"

    parsed_args = None

def parse_args():
    """
    Parse the arguments for the directory to read from and save to.
    """
    # Define what commandline arguments can be accepted
    parser = argparse.ArgumentParser()
    parser.add_argument(Flags.CSV_DIR,metavar="CSV_DIRECTORY", type=check_str_is_dir,
                        help="Source directory containing Digikey CSV files")
    parser.add_argument(Flags.PDF_DIR,metavar="PDF_DIRECTORY", type=check_str_is_dir,
                        help="Directory to save the PDF datasheets to")
    parser.add_argument('--csv_pages', dest=Flags.CSV_PAGES,metavar="NUM_PAGES", type=int, default=1,
                        help="How many 500-row pages to download from Digikey (default 1)")
    parser.add_argument('--fv_code', dest=Flags.FV_CODE,metavar="FV_CODE", default='ffe002af', #op-amp
                        help="The FV code of the part family on Digikey (default op-amps)")
    parser.add_argument('--encrypted', dest=Flags.KEEP_ENCRYPTED, action='store_true', default=False, help="Do not filter encrypted PDFs")
    parser.add_argument('--skip_csv', dest=Flags.SKIP_CSV_DL, action='store_true', default=False, help="Do not redownload the CSV.")
    parser.add_argument('--skip_pdf', dest=Flags.SKIP_PDF_DL, action='store_true', default=False, help="Do not redownload the PDFs.")
    parser.add_argument('--ocr', dest=Flags.KEEP_OCR, action='store_true', default=False, help="Do not filter PDFs that need OCR")
    parser.add_argument('--duplicates', dest=Flags.KEEP_DUPLICATES, action='store_true', default=False, help="Do not filter duplicate PDFs (NOT IMPLEMENTED)")
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.0')
    args = vars(parser.parse_args())

    # TODO (lwhsiao): We should also add option to automatically select a parameterized
    #   number of files and organize as train/test/dev

    Flags.parsed_args = args
    return args

def get_parsed_flags():
    """ Returns the currently parsed flags."""
    return Flags.parsed_args

def keep_encrypted():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.KEEP_ENCRYPTED]

def keep_ocr():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.KEEP_OCR]

def keep_duplicates():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.KEEP_DUPLICATES]

def skip_csv_dl():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.SKIP_CSV_DL]

def skip_pdf_dl():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.SKIP_PDF_DL]

def get_csv_dir():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.CSV_DIR]

def get_pdf_dir():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.PDF_DIR]

def get_csv_pages():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.CSV_PAGES]

def get_fv_code():
    flags_dict = get_parsed_flags()
    return flags_dict[Flags.FV_CODE]

def check_str_is_dir(input_path):
    directory = input_path
    # Check that string has trailing slash
    if not directory.endswith('/'):
         directory + '/'

    # Check for destination directory
    if not os.path.exists(directory):
        raise argparse.ArgumentTypeError("This directory does not exist. Please create it first.")

    return directory
