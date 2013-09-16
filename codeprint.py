#!/usr/bin/env python3

import sys
import os
import argparse
import itertools


# input arguments and defaults
def setup_args():
    """Sets up arguments and defaults, and returns the parsed results"""

    p = argparse.ArgumentParser(
        description="Prepare and format files for printing")

    p.add_argument('-o', '--out', metavar='path', default='printfile',
                   help='specify filename (default: printfile)')
    p.add_argument('-p', '--print', action='store_const',
                   dest='output', const=print_file, default=store_file,
                   help='print the created file immediately')
    p.add_argument('-e', '--reencode', action='store_true',
                   help='explicitly encode the print file in latin1')
    p.add_argument('--header', metavar='txt',
                   default=p.prog + ": " + os.environ['USER'],
                   help='header text, only when printing directly')
    p.add_argument('--language', metavar='lang',
                   help='language to use for syntax highlighting')
    p.add_argument('--printer', metavar='device',
                   help='the printer device to use when printing')
    p.add_argument('--lpp', metavar='int', type=int, default=73,
                   help='lines per printed page')
    p.add_argument('f', metavar='file', nargs='+',
                   help='input files')

    return p.parse_args()


# print the files directly
def print_file(data):
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

    store_file(data)

    print("calling $ enscript{}".format(cmd_args))
    ret = os.system('enscript' + cmd_args)
    print("all done" if ret == 0 else "failed with code {}".format(ret))


def get_font_size(n):
    """takes the number of lines to fit on a page, and returns the
    corresponding font size"""
    if n <= 68:
        return 10
    if n <= 75:
        return 9
    if n <= 83:
        return 8
    else:
        return 7


# store the files in a new file for printing
def store_file(data):
    """takes a string and writes it to a file

    if the reencode option (-e) is given it will use latin-1"""
    try:
        f = open(args.out, "w", encoding='latin1' if args.reencode else None)
        f.write(data)
    except IOError:
        print("Error: could not open "+args.out+" for writing")
        os.exit(1)
    print("output written to file: "+args.out)


# read files
def read_file(fname):
    """reads a file and returns it as a list of lines with a header

    if the file has a sibling with the same name followed by .run it's
    contents will be appended"""
    try:
        file = ["*****************************************\n",
                "* FILE:  {:<30} *\n".format(fname),
                "*****************************************\n"]
        file += [l for l in open(fname, "r")]
        if os.path.isfile(fname+".run"):
            file += ["\n", "*** runtime example ***\n"]
            file += [l for l in open(fname+".run", "r")]
        return file
    except IOError:
        print("Error: "+fname+" is not a file")
        os.exit(1)


# find the optimal order of the files
def align_files(files):
    """Takes a list of *files*, and tries to align them to pages

    The function generates all possible permutations of the list of files,
    and tries position them with at least a few lines between, but aligned to
    the start of the next page if the whole file doesn't fit.

    Each iteration keeps track of how much whitespace is added, and the best
    combination *wins*. If we find a *good* result, the function will finish
    before all permutations are tried."""

    best = 999999
    out = []

    for fs in itertools.permutations(files):
        whitespace = 0          # white space counter
        space = args.lpp        # space available on page
        fset = []               # output candidate, white space is added
                                # between the lines
        for f in fs:
            if (space < (len(f) % args.lpp)):   # alignment whitespace
                fset.append(["\n"] * space)
                whitespace += space

            fset.append(f)                      # add file to candidate
            space = args.lpp - (len(f) % args.lpp)  # space at end of file

            padding = min(2, space)         # add space at end of file
            fset.append(["\n"] * padding)   # but take care not to spill
            space -= padding                # over to next page
                                            # doesn't count as whitespace

        if whitespace < best:       # select best candidate
            best = whitespace
            out = fset
            if best < len(files):   # we accept an average of 1 line per file
                break

    return out


# main
args = setup_args()
files = [read_file(f) for f in args.f]

# rearrange
files = align_files(files)

# output to printer or file
args.output("".join(["".join(f) for f in files]))
