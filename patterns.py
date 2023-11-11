#!/usr/bin/env python3
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


class Abstract:

    def __new__(cls, value, make=True):
        _obj = super().__new__(cls)
        cls.__init__(_obj, value, make)
        if make:
            return _obj.make()
        return _obj

    def __init__(self, value, make=True):
        self.value = value

    def __bool__(self):
        if self._match:
            return True
        return False

    @property
    def _match(self):
        return self.__class__.PATTERN[-1].match(self.value)

    def _find(self, start=None, end=None):
        try:
            for _pattern in self.__class__.PATTERNS[start:end]:
                self.value = _pattern.findall(self.value)[0]
        except IndexError:
            return None
        self.value = self.value[-self.digits:].zfill(self.digits)

    def _sub(self, value, start=None, end=None):
        try:
            for _pattern in self.__class__.PATTERNS[start:end]:
                self.value = _pattern.sub(value, self.value)
        except IndexError:
            return None
        return self.value

    def _merge(self, start=None, end=None):
        for _pattern in self.__class__.PATTERNS[start:end]:
            self.value = _pattern(self.value)
        return self.value


class PatternDecode(Abstract):

    PATTERNS = (('д', 'a'), ('å', 'a'), ('á', 'a'),
               ('ã', 'a'), ('â', 'a'), ('ä', 'a'),
               ('ă', 'a'), ('Å', 'A'), ('Ă', 'A'),
               ('Á', 'A'), ('Ã', 'A'), ('Â', 'A'),
               ('Ä', 'A'), ('é', 'e'), ('ê', 'e'),
               ('ë', 'e'), ('ё', 'e'), ('Ë', 'E'),
               ('É', 'E'), ('Ê', 'E'), ('í', 'i'),
               ('î', 'i'), ('ï', 'i'), ('Í', 'I'),
               ('Î', 'I'), ('Ï', 'I'), ('Ý', 'Y'),
               ('ý', 'y'), ('с', 'c'), ('ć', 'c'),
               ('ç', 'c'), ('Ć', 'C'), ('Ç', 'C'),
               ('С', 'C'), ('з', 'c'), ('ø', 'o'),
               ('ö', 'o'), ('ó', 'o'), ('ô', 'o'),
               ('ð', 'o'), ('Ö', 'O'), ('Ó', 'O'),
               ('Ô', 'O'), ('Ø', 'O'), ('ц', 'u'),
               ('ú', 'u'), ('ü', 'u'), ('û', 'u'),
               ('Ú', 'U'), ('Ü', 'U'), ('Û', 'U'),
               ('п', 'n'), ('ñ', 'n'), ('Ñ', 'N'),
               ('П', 'N'), ('ѕ', 's'), ('š', 's'),
               ('Š', 'S'), ('Ѕ', 'S'), ('ž', 'z'),
               ('Ž', 'Z'), ('ß', 's'), ('ж', 'ae'),
               (' - ', ', '), ('`', '\''), ('’', '\''),
               ('´', '\''), ('\΄', '\''), ('̀', '\''),
               ('’', '\''), ('/', ', '), (';', ', '),
               (':', ', '), ('\\', ', '))

    def make(self):
        for _pattern in self.__class__.PATTERNS:
            self.value = self.value.replace(_pattern[0], _pattern[1])
        return self.value


class PatternBrackets(Abstract):

    PATTERNS = (re.compile("[\[{(]+ *"),
                re.compile(" *[\])}]+"))

    def make(self):
        self._sub("(", 0, 1)
        self._sub(")", 1, 2)
        return self.value


class PatternUnicode(Abstract):

    PATTERNS = "abcdefghijklmnopqrstuvwxyzàèìòùABCDEFGHIJKLMNOPQRSTUVWXYZÀÈÌÒÙ0123456789 &,()'",

    def make(self):
        _value = ""
        for _char in self.value:
            if _char in self.__class__.PATTERNS[0]:
                _value += _char
            else:
                _value += " "
        self.value = _value
        return self.value


class PatternCommas(Abstract):

    PATTERNS = re.compile(" *,+ *"),

    def make(self):
        return self._sub(", ")


class PatternStrip(Abstract):

    def make(self):
        self.value = " ".join(self.value.split())
        return self.value


class PatternLower(Abstract):

    PATTERNS = re.compile("(\w)"),

    def make(self):
        return self._sub(lambda _: _.group(0).lower())


class PatternAccented(Abstract):

    PATTERNS = re.compile("(^| )[Ee]' "),

    def make(self):
        return self._sub(" È ")


class PatternUpper(Abstract):

    PATTERNS = re.compile("(?:^'?|-| |\()(\w)"),

    def make(self):
        return self._sub(lambda _: _.group(0).upper())


class PatternNumerical(Abstract):

    PATTERNS = (re.compile(r"(\d{1,3}),(?=\d{3})"),
                re.compile(r"\d+"))

    @staticmethod
    def format(value, separator="'"):
        if len(value) == 3 or value[0] == "0":
            pass
        else:
            value = "{:,}".format(int(value)).replace(",", separator)
        return value

    def make(self):
        self._sub("\\1", 0, 1)
        self._sub(lambda _: self.format(_.group(0)), 1, 2)
        return self.value


class PatternRockRoll(Abstract):

    PATTERNS = re.compile("rock.{1,5}Roll"),

    def make(self):
        return self._sub("Rock 'n' Roll")


class PatternUselessNumbers(Abstract):

    PATTERNS = re.compile(" ?\((?:[1-9][,\.\']?[0-9]{3}|[0-9]{1,2})\)$"),

    def make(self):
        return self._sub("")


class PatternVolume(Abstract):

    PATTERNS = re.compile(",? +(?:vol\.?|volume?) +(\d{1,2}|[IiVvXx]{1,2})$", re.IGNORECASE),

    def make(self):
        return self._sub(", Vol \\1")


class PatternPart(Abstract):

    PATTERNS = re.compile(" +(?:parte?s?|pts?).? +(\d{1,2}|[IiVvXx]{1,2})"),

    def make(self):
        return self._sub(" Part \\1")


class PatternLive(Abstract):

    PATTERNS = re.compile(" +\(live.*", re.IGNORECASE),

    def make(self):
        return self._sub(" (live)")


class PatternUnplugged(Abstract):

    PATTERNS = (re.compile(" +\(u[nm]plugged.*", re.IGNORECASE),
                re.compile(" +\((?:live |)aco?ustica?.*", re.IGNORECASE))

    def make(self):
        self._sub(" (unplugged)")
        return self.value


class PatternTrait(Abstract):

    PATTERNS = re.compile(" +\((?:inedito|reprise|instrumental|bonus" +
                          "|radio edition|revisited|demo|mono|stereo|remastered" +
                          "|vocal|new studio recordings|edit|unreleased|acapp?ella" +
                          "|unissued|previously unreleased|studio|session outtake" +
                          "|versione?|hidden track|takes? \d{1,2}" +
                          "|remix|demo|extended).*"),


    def make(self):
        return self._sub("")


class PatternFeaturing(Abstract):

    PATTERNS = re.compile("(.*) +\(?(?:[Ff]t|[Ff]eat|[Dd]uett?o? +[Ww]ith|[Ff]eature|[Ff]eaturing" +
                          "|\([Dd]uett?o?|\([Cc]on)\.? ([^\)\(]*)\)?$"),

    def make(self):
        return self._sub("\\1 & \\2")


class PatternAlbum(Abstract):

    PATTERNS = (re.compile(" +\(cds\)", re.IGNORECASE),
                re.compile(" +\([^\)]*deluxe?[^\)]*\).*", re.IGNORECASE),
                re.compile(" +(single|EP|LP)", re.IGNORECASE))

    def make(self):
        self._sub(" (single)", 0, 1)
        self._sub("", 1, 2)
        self._sub(" (\\1)", 2, 3)
        return self.value


class PatternCoded(Abstract):

    PATTERNS = re.compile("^(?:G|RG)$"),

    def make(self):
        if self.__bool__():
            return self.value


class PatternFile(Abstract):

    PATTERN = re.compile("^(?:.*/|)(\d{4}|)(?:-|)([^/]*)/(\d{1,2})-([^-]*)-([^\.]*)(?:\.\w*)$"),

    def make(self):
        if self._match:
            return _match.groups()


class PatternFileBanner(Abstract):

    PATTERN = re.compile("^(.*/|)(\[[A-Z]{3}\]|)([^-]*)-([^-]*)-(\d{4})(\.\w*)$"),

    def make(self):
        _match = self._match
        if _match:
            _match = _match.groups()
            _match = (_match[0],
                     _match[1] or "[ITA]",
                     Title(_match[2]),
                     Title(_match[3]),
                     _match[4], _match[5])
            return "{0}{1} {2}-{3}-{4}{5}".format(*_match)


class Title(Abstract):

    PATTERNS = (PatternLower, PatternDecode,
                PatternUnicode,PatternBrackets,
                PatternCommas, PatternAccented,
                PatternStrip, PatternUpper)

    def make(self):
        return self._merge()


class Mp3Title(Abstract):

    PATTERNS = (PatternLower, PatternDecode,
                PatternUnicode,PatternBrackets,
                PatternCommas, PatternAccented,
                PatternUselessNumbers, PatternRockRoll,
                PatternNumerical, PatternPart,
                PatternTrait, PatternUpper,
                PatternLive, PatternUnplugged,
                PatternStrip)

    def make(self):
        return self._merge()


class Mp3Album(Abstract):

    PATTERNS = (PatternLower, PatternDecode,
                PatternUnicode,PatternBrackets,
                PatternCommas, PatternAccented,
                PatternUselessNumbers, PatternRockRoll,
                PatternNumerical, PatternPart,
                PatternUpper, PatternVolume,
                PatternLive, PatternUnplugged,
                PatternAlbum,
                PatternStrip)

    def make(self):
        return self._merge()
