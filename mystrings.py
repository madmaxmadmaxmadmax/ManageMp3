#!/home/madmax/Scripts/Python/env2/bin/python2.7
# -*- coding: utf-8 -*-
#
#  Copyright 2014 MadMax <madmaxxx@email.it>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

__author__ = 'MadMax'
__version__ = '1.0'
__license__ = 'Public Domain'

import re
import string
import sys
import os
import shutil

CODING = "UTF-8"
CHARSET = "abcdefghijklmnopqrstuvwxyzàèìòùABCDEFGHIJKLMNOPQRSTUVWXYZÀÈÌÒÙ0123456789 &,()'"
REPLACEMENTS = (('д', 'a'),
                ('å', 'a'),
                ('á', 'a'),
                ('ã', 'a'),
                ('â', 'a'),
                ('ä', 'a'),
                ('ă', 'a'),
                ('Å', 'A'),
                ('Ă', 'A'),
                ('Á', 'A'),
                ('Ã', 'A'),
                ('Â', 'A'),
                ('Ä', 'A'),
                ('é', 'e'),
                ('ê', 'e'),
                ('ë', 'e'),
                ('ё', 'e'),
                ('Ë', 'E'),
                ('É', 'E'),
                ('Ê', 'E'),
                ('í', 'i'),
                ('î', 'i'),
                ('ï', 'i'),
                ('Í', 'I'),
                ('Î', 'I'),
                ('Ï', 'I'),
                ('Ý', 'Y'),
                ('ý', 'y'),
                ('с', 'c'),
                ('ć', 'c'),
                ('ç', 'c'),
                ('Ć', 'C'),
                ('Ç', 'C'),
                ('С', 'C'),
                ('з', 'c'),
                ('ø', 'o'),
                ('ö', 'o'),
                ('ó', 'o'),
                ('ô', 'o'),
                ('ð', 'o'),
                ('Ö', 'O'),
                ('Ó', 'O'),
                ('Ô', 'O'),
                ('Ø', 'O'),
                ('ц', 'u'),
                ('ú', 'u'),
                ('ü', 'u'),
                ('û', 'u'),
                ('Ú', 'U'),
                ('Ü', 'U'),
                ('Û', 'U'),
                ('п', 'n'),
                ('ñ', 'n'),
                ('Ñ', 'N'),
                ('П', 'N'),
                ('ѕ', 's'),
                ('š', 's'),
                ('Š', 'S'),
                ('Ѕ', 'S'),
                ('ž', 'z'),
                ('Ž', 'Z'),
                ('ß', 's'),
                ('ж', 'ae'),
                (' - ', ', '),
                ('`', '\''),
                ('’', '\''),
                ('´', '\''),
                ('\΄', '\''),
                ('̀', '\''),
                ('’', '\''),
                ('/', ', '),
                (';', ', '),
                (':', ', '),
                ('\\', ', '))


class Purge:
    PATTERNS = (re.compile("[\[{(]+ *"),
                re.compile(" *[\])}]+"),
                re.compile(" *,+ *"),
                re.compile(unicode("(?:^'?| |\()([a-zàèìòù])", CODING)))

    def __init__(self, value):
        self.value = value

    def decode(self):
        for _index in range(0, len(REPLACEMENTS)):
            self.value = self.value.replace(REPLACEMENTS[_index][0], REPLACEMENTS[_index][1])
        return self.value

    def brackets(self):
        self.value = self.__class__.PATTERNS[0].sub("(", self.value)
        self.value = self.__class__.PATTERNS[1].sub(")", self.value)
        return self.value

    def normalize(self):
        _value = ""
        for _ in self.value.decode(CODING):
            if _ in CHARSET.decode(CODING):
                _value += _
            else:
                _value += " "
        self.value = _value.encode(CODING)
        return self.value

    def commas(self):
        self.value = self.__class__.PATTERNS[2].sub(", ", self.value)
        return self.value

    def strip(self):
        self.value = " ".join(self.value.split())
        return self.value

    def title(self):
        self.value = self.value.decode(CODING)
        self.value = self.__class__.PATTERNS[3].sub(lambda __: __.group(0).upper(), self.value)
        self.value = self.value.encode(CODING)
        return self.value

    def result(self):
        self.decode()
        self.brackets()
        self.normalize()
        self.commas()
        self.strip()
        self.title()
        return self.value
