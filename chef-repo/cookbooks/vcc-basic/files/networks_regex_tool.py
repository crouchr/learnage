# Script to run when parsing a multiline file where capture group needs to be identified
# Workflow : wrangle/test your regex in regex101.com (select Python flavour of regex) and then use this script to
# simplify the capture group extraction
# This runs on WAF (Centos7) and therefore uses Python 2.7
from __future__ import print_function

import re
import sys


def do_it(text, regex, match_group_index):
    """
    Run the regex over the text (can be multiline) and return the match_group_index capture_group
    exit 2 if failed to locate the capture group
    :param text:
    :param regex:
    :param match_group_index:
    :return:
    """
    try:
        capture_groups = re.findall(regex, text)
        if len(capture_groups) == 0:
            sys.exit(3)     # 3 == no match found
        x = capture_groups[0][match_group_index]
        x = x.rstrip()      # remove the trailing \n
        return x

    except Exception as e:
        print('exception : ' + e.__str__())
        sys.exit(5)         # 5 == an exception, i.e. user error


def main():
    # use these lines when developing
    # filename = 'httpd-test-002.conf'
    # regex = r"(?:Admin > \s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)"
    # regex = r"(?:Location \"\/server-status\">\s+SetHandler server-status\s+Require local\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)"
    # capture_group_index = 0

    if len(sys.argv) == 1:
        print("usage : networks_regex_tool.py <filename> <regex> <capture_group_index>")
        sys.exit(4)

    filename = sys.argv[1]
    regex = sys.argv[2]
    capture_group_index = int(sys.argv[3])

    #print("filename : " + filename.__str__())
    #print("regex : " + regex.__str__())
    #print("capture_group : " + capture_group_index.__str__())

    with open(filename, 'r') as f:
        file_text = f.read()
        capture_group = do_it(file_text, regex, capture_group_index)

    # print so external program can pick it up, do not add the training \n
    print(capture_group.__str__(), end='')


if __name__ == '__main__':
    main()
