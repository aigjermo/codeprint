============
codeprint.py
============

codeprint is meant primarily for printing out sets of small scripts.

It will try to place the texts so that they only break across pages when
necessary and prefers to move them to the next page when the whole file 
can't.

The output file should be suitable for printing with f.eks :hardcopy in vim,
which outputs 73 lines per page on my system (which is the default here).


Runtime examples
----------------

When the program reads a file it will look for runtime examples with the same
filename plus the extension .run. If such a file is found it will be appended
with after the main file, separated by a marker:
*** runtime example ***


Parameters
==========

-o, --out <file>        write output to the specified file
                        the default output is "printfile"

-p, --print             print the file immediately (see useful options below)

-e, --reencode          use latin-1 for the output file, this might be needed
                        on utf-8 systems when printing directly

--header text           header text for the print when printing directly
                        This defaults to "codeprint.py: username"

--language lang         Specify the language for the syntax highlighting

--lpp int               The number of lines per page to use for positioning
                        The default is 73 lines.


Dependencies
============

The script uses enscript to print directly, but you can still compose files
without having it installed.


Installation
============

Clone this repository or download the tar and unpack, then install with

    python3 setup.py install
