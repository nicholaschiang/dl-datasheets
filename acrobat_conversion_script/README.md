# Converting PDFs to HTML

Currently, we need Adobe Acrobat to convert PDFs to HTML.
The output it produces is _not_ very nice. However, it is the best we currently have.

This folder contains the [Automa](http://www.getautoma.com/) used in Windows to convert PDFs to HTML.

These scripts assume that there is a `sanitize-to-html` custom Action already set up.
This action is setup in the Action wizard, and takes a folder of PDF as input, sanitizes then and saves these into a separate folder, and then converts them to HTML into a third folder.

We need this script because Acrobat DC and Acrobat XI both crash on long-running jobs.
