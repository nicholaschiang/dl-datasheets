#!/bin/bash

# if [[ -z "$1" || -z "$2" ]]; then
#   echo 'Usage: ./filter_search.sh <raw_pdf_dir> <search_term>'
#   exit
# fi


function pdfsearch()
{
    rm bad_files.txt
    find . -iname '*.pdf' | while read filename
    do
        # echo -e "\033[34;1m// === PDF Document:\033[33;1m $filename\033[0m"
        pdftotext -q "$filename" "$filename.txt"
        # grep -l -i "zener" "$filename" | xargs -r rm
        grep -l -i "digital transistor" "$filename.txt" | tee -a bad_files.txt
        rm "$filename.txt"
    done

    # cat bad_files.txt | while read line
    # do
    #   bad_file="${line:0:-4}" # remove ".txt"
    #   rm "$bad_file"
    # done
    # rm bad_files.txt
}

pdfsearch

# NOTE: Steps taken when cleaning up the combined data
#   - removed all PDFs containing 'rectifie'
#   - removed all PDFs containing 'zener'
#   - removed all PDFs containing 'sensor'
#   - removed all PDFs containing 'operational amplifier'
#   - removed all PDFs containing 'phototransistor'
#   - removed all PDFs containing 'op amp'
#   - removed all PDFs containing 'rationmetric'
#   - removed all PDFs containing 'transceiver'
#   - removed all PDFs containing 'microprocessor'
#   - removed all PDFs containing 'select pin'
#   - removed all PDFs containing 'voltage reference'
#   - removed all PDFs containing 'gate voltage'
#   - removed all PDFs containing 'reverse breakdown'
#   - removed all PDFs containing 'voltage suppressor'
