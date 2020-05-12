#/usr/bin/python

import string

myStr = "1234djsj"
a = "".join(s for s in myStr if s in string.printable)

print myStr
print a
