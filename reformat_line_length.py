# Written using Python 3.7.3
# (i.e., Assignment Expressions or proper Type Hints cannot be applied yet)
""" Reformat files to a specified line length.

The script can try to detect manual linebreaks and preserve these, preserve
empty lines, accept characters where words are allowed to be broken, and
consider characters at the start of a new line to detect further manual
linebreaks.
\\
If no new line length is specified, this number is set based on the longest
line from the input file. Not specifying a line length and letting the script
try to detect manual linebreaks essentially results in no effect, except for
the possible removal of some trailing whitespaces.
"""

import os
import argparse
# more specific imports possible, e.g., `from argparse import ArgumentParser`


def get_cmd_line_args():
    """ Initiate command line arguments via `argparse`.

    Returns the Namespace from the argparse module's ArgumentParser, which
    includes all parameters and their values.
    """
    ## PARAMETER ROADMAP:
    # paths: Optional[list] = None
    # ncol: Optional[int|list[int]] = None # check whether list or int, if int 
    #                                      # apply length to all chosen files, 
    #                                      # if list of ints, check if length
    #                                      # matches length of paths and apply
    #                                      # on per path basis
    #                                      # ==> MAYBE BETTER FOR NOW: stick to
    #                                      # a single number, but implement
    #                                      # this as a list with that number
    #                                      # for each path, such that a later
    #                                      # change is easier to implement
    # breakchars: Optional[list[str]] = ['-', '/']
    # startchars: Optional[list[str]] = [' ', '-', '*', '>', '\t']
    # preserve_breaks: Optional[bool] = True
    # --> AS A FLAG: ignore_manual_breaks; IF NOT SET: False; IF SET: True
    # preserve_empty_lines: Optional[bool] = True
    # --> AS A FLAG: remove_empty_lines; IF NOT SET: False; IF SET: True
    parser = argparse.ArgumentParser(
        description="Reformat files to a specified line length."
    )
    parser.add_argument("paths", type=str, nargs="+", default=None,
                        help="paths to files which are to be reformatted")
    parser.add_argument("--ncol", type=int, nargs="?", default=None,
                        help="new maximum line length")
    parser.add_argument("--breakchars", type=str, nargs="*",
                        default=['-', '/'], help=("characters other than "
                                                  "whitespaces where "
                                                  "linebreaks are allowed; "
                                                  "defaults: '-', '/'"))
    parser.add_argument("--startchars", type=str, nargs="*",
                        default=[' ', '-', '*', '>', '\t'],
                        help=("characters at the start of a line that "
                              "indicate a manual linebreak; defaults: ' ', "
                              "'-', '*', '>', '\\t'"))
    parser.add_argument("-b", "--ignore_manual_breaks", action="store_true",
                        help=("avoid detection of manual linebreaks and "
                              "preservation of these"))
    parser.add_argument("-r", "--remove_empty_lines", action="store_true",
                        help=("remove empty lines (whitespaces count as "
                              "content)"))
    return parser.parse_args()
    ## accessing arguments - example:
    # args = parser.parse_args() # `args` is now a Namespace that includes the
    #                            # arguments without any leading hyphen, e.g.,
    #                            # access the '-r' or '--remove_empty_lines'
    #                            # argument using its name 'remove_empty_lines'
    #                            # via `args.remove_empty_lines`
    # EXAMPLE: (here, neither -r nor --remove_empty_lines is used)
    # IN: print(f"remove_empty_lines = {args.remove_empty_lines}")
    # OUT: remove_empty_lines = False

def yn_prompt(prompt: str, default: str = None, verbose: bool = False) -> bool:
    """
    A short function to give the user a prompt and ask yes-or-no. It is pos-\\
    sible to choose a default answer, which is then indicated automatically.

    Parameters:
    -----------
    prompt : str
        A user prompt, typically a question, which has a yes-or-no answer.
    default : str: [`'y'`, `'yes'`] / [`'n'`, `'no'`]
        If one of the options is given the respective default setting is in-
        dicated. Otherwise default is set to `None` and no answer is indicated.
    verbose : bool
        Toggle printing of information for some special cases.

    Returns:
    --------
    Depending on the user's choice returns a boolean value: `True` for yes and
    `False` for no.

    Dependencies:
    -------------
    None
    """
    if default is None:
        deflt, opt = " [y/n] ", -1
    else:
        if not isinstance(default, str):
            raise Exception("Parameter `default` must be class `str`.")
        if default.lower() in ['y', 'yes']:
            deflt, opt = " [Y/n] ", 1
        elif default.lower() in ['n', 'no']:
            deflt, opt = " [y/N] ", 0
        else:
            if verbose:
                print("`default` parameter not recognized.")
            deflt, opt = " [y/n] ", -1

    while True:
        inp = input(prompt + deflt)
        if (not inp and opt==1) or inp.lower().startswith('y'):
            re = True
            break
        elif (not inp and opt==0) or inp.lower().startswith('n'):
            re = False
            break
        else:
            if verbose:
                print("Not understood. Please try again.")
            continue
    return re

def check_paths(paths: list) -> list:
    """ Test if given paths lead to valid files. """
    invalid_paths = [p for p in paths if not os.path.isfile(p)]
    if len(invalid_paths) > 0 : # `if invalid_paths:` would work as well
        if len(paths) == len(invalid_paths):
            print("No valid paths given (no file found).\nreturn None")
            return None
        print("Following paths are invalid (no file found):")
        for ip in invalid_paths:
            print(f" {ip}")
        if yn_prompt("Continue without invalid paths?", "y"):
            print("Using valid paths only.")
            return [p for p in paths if p not in invalid_paths]
        else:
            print("return None")
            return None
    return paths # essentially the else case where all paths are valid

def new_filename(path: str) -> str:
    """ Find a new filename, which does not exist yet. """
    basename = os.path.basename(path)
    path_only = path[:-len(basename)]
    name, ext = basename.rsplit('.')
    counter = 1
    while os.path.isfile(path_only+name+f"_{counter}.{ext}"):
        counter += 1
    return path_only+name+f"_{counter}.{ext}"

def reformatter(
        path: str, ncol: int = None, preserve_breaks: bool = True,
        preserve_empty_lines: bool = True, breakchars: list = ['-', '/'],
        startchars: list = [' ', '-', '*', '>', '\t']
        ) -> list:
    """Reformat file contents to a given line length.

    Parameters:
    -----------
    path : str
        Full or relative path to a file that should be reformatted.
    ncol (optional) : int, default = None
        Number of columns after reformatting, i.e., the line length. If not
        specified the length of the longest line in the input file is used.
    preserve_breaks (optional) : bool, default = True
        Try to find manually set linebreaks by using the length of the longest
        line in the input file. Does not overwrite the parameter `startchars`!
    preserve_empty_lines (optional) : bool, default = True
        Keep empty lines (whitespaces count as content) or remove them.
    breakchars (optional) : list, default = ['-', '/']
        Decide whether linebreaks can occur at the given characters. These
        characters are not removed, but stay at the end of the line that is
        broken.
    startchars (optional) : list, default = [' ', '-', '*', '>', '\\t']
        Single characters that indicate a manual linebreak if leading the
        following line, i.e., even if they still fit on the previous line,
        they should be kept at the start of the next line.
    
    Returns:
    --------
    list[str]
        A list of strings, where each string represents a reformatted line.

    Dependencies:
    -------------
    None
    """

    ## code idea (reason for not using it as text within)
    '''
    new_path = new_filename(path)
    with open(path, 'r') as infile, open(new_path, 'a') as outfile:
        print(
            "Do things here, but this created already a new, empty file. "
            "While that can be deleted by the lower code, any exception or "
            "error means that those lines are never reached. Thus, I prefer "
            "the handling of the full file contents within a python object, "
            "despite the fact that the contents then need to be fully saved "
            "in memory."
            )
    if os.stat(new_path).st_size == 0:
        os.remove(new_path)
    '''

    ## removed this snippet to avoid user interaction in a computation function
    '''
    ## avoid unnecessary computation for "bad" parameter settings
    if ncol is None and preserve_breaks:
        print("No line length specified and manual breaks are supposed to "
              "be preserved. This might result in no effective change, except "
              "for the removal of some trailing whitespaces.",
              end=' ')
        if not yn_prompt("Continue?", 'y'):
            # user choice is 'no', i.e., do not continue
            raise SystemExit("aborted")
        else:
            print("continue")
    '''

    with open(path, 'r') as infile:
        if preserve_empty_lines:
            content = [line for line in infile]
        else: # remove empty lines (whitespaces count as content!)
            content = [line for line in infile if line[:-1]]
    
    # save each line's length
    line_lengths = [len(line)-1 for line in content]
    # find longest line (not counting trailing whitespaces)
    max_len = max(line_lengths)

    if ncol is None:
        ncol = max_len # not really useful if `preserve_breaks` is True

    for n in range(len(content)):
        tmp_line = []
        word = []
        for char in content[n]:
            if char == ' ':
                tmp_line.append([''.join(word), ''])
                word = []
            elif char in breakchars:
                tmp_line.append([''.join(word), char])
                word = []
            elif char == '\n' and word:
                tmp_line.append([''.join(word), ''])
            else:
                word.append(char)
        if not tmp_line: # empty line
            tmp_line.append(['', '\n'])
        tmp_line.append({'old_len':line_lengths[n]})
        content[n] = tmp_line
    # At this point each line is a list that contains for each word a sublist.
    # Each sublist is the current word and a str that indicates the following
    # character after the word, e.g., '-' for a hyphen or the empty str '' for
    # a whitespace.
    # The line list has a dictionary as its last item, which contains the key
    # 'old_len', that describes the length of the line before any changes.

    # add the length of each word to its respective list
    for n in range(len(content)):
        for i in range(len(content[n])-1):
            content[n][i].append(len(content[n][i][0]))
    # Now each word sublist is extended by the length of each word.

    # mark linebreaks as either fixed or modifiable
    for n in range(len(content)-1):
        try:
            # check start of next line
            if ((content[n+1][0][1] == '\n') # empty line
                or (not content[n+1][0][0] and not content[n+1][0][1]
                    and ' ' in startchars) # whitespace & it is a startchar
                or (not content[n+1][0][0] and content[n+1][0][1] in
                    startchars) # lone breakchar, which is also a startchar
                or (preserve_breaks and (content[n+1][0][2]
                    + content[n][-1]['old_len'] <= max_len)) # next word ...
                    # ... would still fit on current line
                ):
                content[n][-1]['manual_break'] = True
            # Separate the case of any other leading startchar from the other
            # conditions to underline that this is where the IndexError can
            # occur. The order of conditions is important to catch the error
            # properly!
            elif (content[n+1][0][0][0] in startchars):
                content[n][-1]['manual_break'] = True
            else:
                content[n][-1]['manual_break'] = False
        # If next word is '' it has no 0th index, i.e., when trying to call
        # `content[n+1][0][0][0]` it throws an IndexError. This is only
        # encountered if a line starts with a whitespace, but a whitespace
        # is not found within the startchars.
        except IndexError:
            content[n][-1]['manual_break'] = False
    # for completeness add a manual_break dict key for the last line as well
    content[-1][-1]['manual_break'] = False
    # The trailing dictionary in each line list now also contains the key
    # 'manual_break', which indicates whether this line is supposed to be
    # broken there or can be rearranged.

    ## The following code snippet could be avoided, by not using the dict key
    ## 'manual_break' at all, but inserting the linebreak directly instead.
    ## As the logic of this code changed a few times, keep this for now. It
    ## might make sense to change this later to avoid unnecessary overhead.
    for n in range(len(content)):
        if ((content[n][-1]['manual_break'] is True) # detect manual linebreaks
            and not (content[n][0][1] == '\n') # but skip empty lines
            ):
            # insert linebreak as last word-list in the line-list
            content[n] = content[n][:-1] + [['','\n',0]] + [content[n][-1]]

    # rearrange the lines into one large stream of word-lists (w/o the dicts)
    content = [wlist for line in content for wlist in line[:-1]]

    # check for a trailing new line & add it (if necessary) for easier handling
    # in the next stages
    artificial_newline = False
    if not content[-1][1] == '\n':
        artificial_newline = True
        content += [['', '\n', 0]]

    # apply the new length by creating lines up this respective length
    new_content = []
    curr_line = []
    new_length = 0
    while True:
        if content: # effectively: `len(content) > 0`
            curr_word = content.pop(0)
        else: # content is empty
            if curr_line: # current line contains content from the last line
                new_content.append(curr_line)
            break
        if not curr_word[0]: # lone whitespace or breakchar, or new line
            if curr_word[1] == '\n': # manual new line
                curr_line.append(curr_word[:-1])
                new_content.append(curr_line)
                curr_line = []
                new_length = 0
                continue
            # otherwise: lone whitespace or breakchar
            elif new_length+1 <= ncol:
                curr_line.append(curr_word[:-1])
                new_length += 1
                continue
            else: # max allowed length would be exceeded
                curr_line.append(['', '\n'])
                new_content.append(curr_line)
                curr_line = [curr_word[:-1]]
                new_length = 1
                continue
        else: # the word contains at least one character
            # word is followed by a whitespace and still fits in line
            if not curr_word[1] and new_length+curr_word[2] <= ncol:
                curr_line.append(curr_word[:-1])
                new_length += curr_word[2]+1
                continue
            # word is followed by a breakchar and still fits in line
            elif curr_word[1] and new_length+curr_word[2]+1 <= ncol:
                curr_line.append(curr_word[:-1])
                new_length += curr_word[2]+1
                continue
            else: # line is full
                curr_line.append(['', '\n'])
                new_content.append(curr_line)
                curr_line = [curr_word[:-1]]
                new_length = curr_word[2]+1
                continue
    # # remove trailing new line at the end
    # new_content[-1] = new_content[-1][:-1]
    # -> keep the trailing new line here for easier handling in the next stage

    # concatenate word-lists into one string per line
    for n in range(len(new_content)):
        tmp_line = ''
        for i,w in enumerate(new_content[n]): # i: index, w: word(-list)
            if not w[0]: # word itself is empty
                if w[1] == '\n': # end of current line
                    tmp_line += w[1]
                    new_content[n] = tmp_line
                    break # for readability only (should be superfluous)
                elif not w[1]: # lone whitespace
                    tmp_line += ' '
                    continue
                else: # lone breakchar
                    tmp_line += w[1]
                    continue
            else: # word contains at least one character
                # current word is last in line and trailed by a whitespace
                if new_content[n][i+1][1]=='\n' and not w[1]:
                    tmp_line += w[0]
                    continue
                # word is trailed by a whitespace
                elif not w[1]:
                    tmp_line += w[0]+' '
                    continue
                # word is trailed by a breakchar
                else:
                    tmp_line += w[0]+w[1]
                    continue

    # remove the very last newline-char, if it was added artificially
    if artificial_newline:
        new_content[-1] = new_content[-1][:-1]

    ## The whole content could be pushed into one large string, which has
    ## newline characters at the right places. However, keep it as a string per
    ## line for now, as 1: not expecting extremely large files where memory
    ## issues arise, 2: better overview when maintaining the code (debugging/
    ## printing results), 3: in the unlikely case of working on performance
    ## enhancements it might be possible to write directly on a per-line basis
    ## instead of accumulating the contents and then writing these later on.

    # return new_content

    with open(new_filename(path), 'a') as outfile:
        for line in new_content:
            outfile.write(line)

def main():
    """ main (module wrapper) """

    args = get_cmd_line_args()

    check_paths(args.paths)

    ncols = [args.ncol]*len(args.paths)
    paths_ncols = list(zip(args.paths, ncols))
    ## `path_ncol` contains tuples of one filename and one ncol. This is used
    ## instead of applying the single ncol directly, in order to enable an
    ## easier modification, in case ncol is supposed to be optionally a list of
    ## different numbers (one for each path). Then, only the line that creates
    ## `ncols` needs to be modified, but other code still works just fine.

    for path_ncol in paths_ncols:
        reformatter(
            path = path_ncol[0],
            ncol = path_ncol[1],
            preserve_breaks = not args.ignore_manual_breaks,
            preserve_empty_lines = not args.remove_empty_lines,
            breakchars = args.breakchars,
            startchars = args.startchars
        )

    return


if __name__ == "__main__":

    ## TESTING of the `reformatter` function
    # curr_test_path = "./test_file2_copy.txt" # path to a local test file
    # reformatter(curr_test_path)

    main()