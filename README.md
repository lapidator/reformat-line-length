From the file's docstring:

> Reformat files to a specified line length.
> 
> The script can try to detect manual linebreaks and preserve these, preserve
> empty lines, accept characters where words are allowed to be broken, and
> consider characters at the start of a new line to detect further manual
> linebreaks.
> 
> If no new line length is specified, this number is set based on the longest
> line from the input file. Not specifying a line length and letting the script
> try to detect manual linebreaks essentially results in no effect, except for
> the possible removal of some trailing whitespaces.


## Usage

`reformat_line_length.py [-h] [--ncol [NCOL]] [--breakchars [BREAKCHARS [BREAKCHARS ...]]] [--startchars [STARTCHARS [STARTCHARS ...]]] [-b] [-r] paths [paths ...]`  
Use the `-h` flag for more information on each argument.

As an example:  
Reformat two files (/path/to/file1 and /path/to/file2) to have a new maximum line length of 80 characters, while the script should *not* try to detect manual linebreaks, but ignore these instead.  
Shell command: `python reformat_line_length.py /path/to/file1 /path/to/file2 --ncol 80 -b`
