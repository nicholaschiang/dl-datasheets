#!/bin/bash

# Some PDFs are encrypted, and we cannot open it directly in the table-extraction parser. This decrypts an entire directory.

if [[ -z "$1" || -z "$2" ]]; then
  echo 'Usage: ./decrypt.sh <raw_pdf_dir> <output_dir>'
  exit
fi
#pdfs="$(find $1 -maxdepth 1 -iname '*.pdf')"
mkdir -p $2

function dpdf {
  f=$1
  encrypted="$(pdfinfo $f 2>&1 | grep -P 'Encrypted: *yes')"
  if [[ "$encrypted" ]]; then
    # NOTE: If it has ever been encrypted, Adobe Acrobat crashes when trying to
    # convert the PDF to HTML. So, if it's been encrypted, just completely
    # ignore it by commenting out the lines below.
    # outpdf="$(basename $f)"
    # outpdf="$2/$outpdf"
    # echo "Decrypting $f"
    # gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=$outpdf -c .setpdfwrite -f $f
  else
    echo "Copying $f to $2"
    cp $f $2
  fi
}
export -f dpdf
find $1 -maxdepth 1 -iname '*.pdf' | xargs -n 1 -P 20 -I {} bash -c 'dpdf "$1" '$2 _ {}
