#!/usr/bin/env python3
""" codeprint.py

functions to align a set of text files on as few pages as possible, while
avoiding pagebreaks in files where possible
"""

import os
import sys
import argparse
import itertools


# input arguments and defaults
def setup_args():
    """Sets up arguments and defaults, and returns the parsed results"""

    par = argparse.ArgumentParser(
        description="Prepare and format files for par.inting")

    par.add_argument('-o', '--out', metavar='path', default='printfile',
                   help='specify filename (default: par.intfile)')
    par.add_argument('-p', '--print', action='store_const',
                   dest='output', const=print_file, default=store_file,
                   help='print the created file immediately')
    par.add_argument('-e', '--reencode', action='store_true',
                   help='explicitly encode the par.int file in latin1')
    par.add_argument('--header', metavar='txt',
                   default=par.prog + ": " + os.environ['USER'],
                   help='header text, only when par.inting directly')
    par.add_argument('--language', metavar='lang',
                   help='language to use for syntax highlighting')
    par.add_argument('--printer', metavar='device',
                   help='the par.inter device to use when par.inting')
    par.add_argument('--lpp', metavar='int', type=int, default=73,
                   help='lines par.r par.inted par.ge')
    par.add_argument('f', metavar='file', nargs='+',
                   help='input files')

    return par.parse_args()


# print the files directly
def print_file(args, data):
    """prints the given string with enscript

    print options depend on the arguments given to the script"""

    cmd_args = (" --pretty-print --color -L {0} --header \"{1}"
                "||Page $% of $=\" -f Courier{2}")
    cmd_args = cmd_args.format(args.lpp, args.header, get_font_size(args.lpp))
    if args.printer:
        cmd_args += " -d {}".format(args.printer)
    if args.language:
        cmd_args += " -E{}".format(args.language)
    cmd_args += " " + args.out

    store_file(args, data)

    print("calling $ enscript{}".format(cmd_args))
    ret = os.system('enscript' + cmd_args)
    print("all done" if ret == 0 else "failed with code {}".format(ret))


def get_font_size(lpp):
    """takes the number of lines to fit on a page, and returns the
    corresponding font size"""
    if lpp <= 68:
        return 10
    if lpp <= 75:
        return 9
    if lpp <= 83:
        return 8
    else:
        return 7


# store the files in a new file for printing
def store_file(args, data):
    """takes a string and writes it to a file

    if the reencode option (-e) is given it will use latin-1"""
    try:
        out = open(args.out, "w", encoding='latin1' if args.reencode else None)
        out.write(data)
        out.close()
    except IOError:
        print("Error: could not open "+args.out+" for writing")
        sys.exit(1)
    print("output written to file: "+args.out)


# read files
def read_file(fname):
    """reads a file and returns it as a list of lines with a header

    if the file has a sibling with the same name followed by .run it's
    contents will be appended"""
    try:
        out = ["*****************************************\n",
                "* FILE:  {:<30} *\n".format(fname),
                "*****************************************\n"]
        out += [l for l in open(fname, "r")]
        if os.path.isfile(fname+".run"):
            out += ["\n", "*** runtime example ***\n"]
            out += [l for l in open(fname+".run", "r")]
        return out
    except IOError:
        print("Error: "+fname+" is not a file")
        sys.exit(1)


# find the optimal order of the files
def align_files(files, lpp):
    """Takes a list of *files*, and tries to align them to pages

    The function generates all possible permutations of the list of files,
    and tries position them with at least a few lines between, but aligned to
    the start of the next page if the whole file doesn't fit.

    Each iteration keeps track of how much whitespace is added, and the best
    combination *wins*. If we find a *good* result, the function will finish
    before all permutations are tried."""

    best = 999999
    out = []

    for fileset in itertools.permutations(files):
        whitespace = 0          # white space counter
        space = lpp             # space available on page
        cand = []               # output candidate, white space is added
                                # between the lines
        for txt in fileset:
            if (space < (len(txt) % lpp)):   # alignment whitespace
                cand.append(["\n"] * space)
                whitespace += space

            cand.append(txt)                  # add file to candidate
            space = lpp - (len(txt) % lpp)    # space at end of file

            padding = min(2, space)         # add space at end of file
            cand.append(["\n"] * padding)   # but take care not to spill
            space -= padding                # over to next page
                                            # doesn't count as whitespace

        if whitespace < best:       # select best candidate
            best = whitespace
            out = cand
            if best < len(files):   # we accept an average of 1 line per file
                break

    return out


def main():
    """ Reads the files, aligns them and calls the output function """
    args = setup_args()
    files = [read_file(f) for f in args.f]

    # rearrange
    files = align_files(files, args.lpp)

    # output to printer or file
    args.output(args, "".join(["".join(f) for f in files]))


if __name__ == "__main__":
    main()
