#
#  utils.py
#
# Author: Jeremy Tidemann <jeremy@hologram.io>
#
# License: Copyright (c) 2016 Hologram All Rights Reserved.
#
# Released under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def printable_string(input_string):
    """ Return a string (unicode or ascii) that is safe to use with print() or str()

    This provides functionality is similar to `str()` but with the added benefit
    of converting an input to a unicode string if it has unicode characters. If successful,
    the string returned will be safe to use with printf() and str() functions, even
    if it originally contained unicode characters.

    Args:
        input (str, unicode): Input string

    Returns:
        str: A string safe to use with printf() and str() functions

    """
    try:
        output_string = str(input_string)
    except UnicodeError:
        output_string = input_string.encode('utf8', 'replace')
    return output_string

