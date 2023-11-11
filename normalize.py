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
import config
import mystrings
import shutil
import sys
import os


class AbstractFind(object):

    def __init__(self, value, digits):
        self.value = value
        self.digits = digits

    def purge(self):
        pass

    def normalize(self):
        try:
            for _pattern in self.__class__.PATTERNS[:-1]:
                self.value = _pattern.findall(self.value)[0]
        except IndexError:
            return None
        self.value = self.value[-self.digits:].zfill(self.digits)
        if self.__class__.PATTERNS[-1].match(self.value):
            return self.value
        return None


class AbstractSub(object):

    def __init__(self, value, digits):
        self.value = value

    def purge(self):
        self.value = mystrings.Purge(self.value).result()

    def normalize(self, start=None, end=None):
        try:
            for _pattern, _sub in self.__class__.PATTERNS[start:end]:
                self.value = _pattern.sub(_sub, self.value)
        except IndexError:
            return None
        return self.value


def numerical_format(arg, separator="'"):
    if len(arg) == 3 or arg[0] == "0":
        return arg
    return "{:,}".format(int(arg)).replace(",", separator)


class Patterns(object):

    PATTERNS = (re.compile(r"([0-9]{1,3}),(?=[0-9]{3})"),
                re.compile(r"\d+"),
                re.compile("[Rr]ock.{1,5}[Rr]oll"),
                re.compile("^[Ee]' "),
                re.compile(" [Ee]' "),
                re.compile(" ?\((?:[1-9][,\.\']?[0-9]{3}|[0-9]{1,2})\)$"),
                re.compile(",? +(?:[Vv]ol\.?|[Vv]olume?) +([0-9]{1,2}|[IiVvXx]{1,2})$"),
                re.compile(" +(?:[Pp]arte?s?|[Pp]ts?).? +([0-9]{1,2}|[IiVvXx]{1,2})"),
                re.compile(" +\([Ll]ive.*$"),
                re.compile(" +\([Uu][nm]plugged.*$"),
                re.compile(" +\((?:[Ll]ive |)[Aa]co?ustica?[^\)\(]*\)$"),
                re.compile("(.*) +\(?(?:[Ff]t|[Ff]eat|[Dd]uett?o? +[Ww]ith|[Ff]eature|[Ff]eaturing" +
                           "|\([Dd]uett?o?|\([Cc]on)\.? ([^\)\(]*)\)?$"),
                re.compile(" +\((?:[Ii]nedito|[Rr]eprise[^\)]*|[Ii]nstrumental|[Bb]onus [Tt]rack[^\)]*|[Bb]onus" +
                           "|[Rr]adio [Ee]dition|[Rr]evisited|[Dd]emo|[Mm]ono|[Ss]tereo|[Rr]emastered" +
                           "|[Vv]ocal|[Nn]ew [Ss]tudio [Rr]ecordings|[Ee]dit|[Uu]nreleased|[Aa]capella"
                           "|Unissued|[Pp]reviously [Uu]nreleased|[Ss]tudio|[Ss]ession [Oo]uttake)\)$"))

    def __init__(self, string):
        self._string = string

    def pattern_numerical(self):
        self._string = self.__class__.PATTERNS[0].sub("\\1", self._string)
        self._string = self.__class__.PATTERNS[1].sub(lambda index: numerical_format(index.group(0)), self._string)
        return self._string

    def pattern_rock_roll(self):
        self._string = self.__class__.PATTERNS[2].sub("Rock 'n' Roll", self._string)
        return self._string

    def pattern_accented(self):
        self._string = self.__class__.PATTERNS[3].sub("È ", self._string)
        self._string = self.__class__.PATTERNS[4].sub(" È ", self._string)
        return self._string

    def pattern_useless_numbers(self):
        self._string = self.__class__.PATTERNS[5].sub("", self._string)
        return self._string

    def pattern_volume(self):
        self._string = self.__class__.PATTERNS[6].sub(", Vol \\1", self._string)
        return self._string

    def pattern_part(self):
        self._string = self.__class__.PATTERNS[7].sub(" Part \\1", self._string)
        return self._string

    def pattern_live(self):
        self._string = self.__class__.PATTERNS[8].sub(" ({})".format(config.TYPES[1]), self._string)
        return self._string

    def pattern_unplugged(self):
        self._string = self.__class__.PATTERNS[9].sub(" ({})".format(config.TYPES[2]), self._string)
        self._string = self.__class__.PATTERNS[10].sub(" ({})".format(config.TYPES[2]), self._string)
        return self._string

    def pattern_featuring(self):
        self._string = self.__class__.PATTERNS[11].sub("\\1 & \\2", self._string)
        return self._string

    def match_featuring(self):
        if self.__class__.PATTERNS[11].match(self._string[1]):
            self._string = ("{} & {}".format(self._string[0], self.__class__.PATTERNS[11].sub("\\2", self._string[1])),
                            self.__class__.PATTERNS[11].sub("\\1", self._string[1]))
        return self._string

    def pattern_trait(self):
        while True:
            _string = self.__class__.PATTERNS[12].sub("", self._string)
            if _string == self._string:
                break
            self._string = _string
        return self._string

    def get_string(self):
        return self._string


class Artist(object):

    def __init__(self, artist, title):
        self._artist = artist
        self._title = title

    def purge(self):
            self._artist = mystrings.Purge(self._artist).result()
            self._title = mystrings.Purge(self._title).result()

    def normalize(self):
        self._artist = Patterns(self._artist).pattern_featuring()
        self._artist, self._title = Patterns((self._artist, self._title)).match_featuring()
        self._artist = Patterns(self._artist).pattern_numerical()
        return self._artist, self._title


class Title(object):

    PATTERNS = re.compile(" +\((?:[Vv]ersione? +[^ ]*|[Hh]idden +[Tt]rack|.{1,2}|[^\)]*[Tt]akes? +[0-9]{1,2}[^\)]*" +
                          "|[^\)]*[Rr]emix[^\)]*|[Dd]emo +[^\)]*|[Ee]xtended[^\)]*)\)$"),

    def __init__(self, title):
        self._title = title

    def purge(self):
        self._title = mystrings.Purge(self._title).result()

    def normalize(self):
        self._title = self.__class__.PATTERNS[0].sub("", self._title)
        _title = Patterns(self._title)
        _title.pattern_part()
        _title.pattern_useless_numbers()
        _title.pattern_accented()
        _title.pattern_numerical()
        _title.pattern_rock_roll()
        _title.pattern_unplugged()
        _title.pattern_live()
        _title.pattern_trait()
        return _title.get_string()


class Album(object):

    PATTERNS = (re.compile(" +[\(\[\{]?CDS[\)\]\}]?$"),
                re.compile(" +([Ss]ingle|[Ee][Pp]|[Ll][Pp])$"))

    def __init__(self, album):
        self._album = album

    def purge(self):
        self._album = mystrings.Purge(self._album).result()

    def normalize(self):
        self._album = self.__class__.PATTERNS[0].sub(" (Single)", self._album)
        self._album = self.__class__.PATTERNS[1].sub(" (\\1)", self._album)
        _album = Patterns(self._album)
        _album.pattern_part()
        _album.pattern_volume()
        _album.pattern_useless_numbers()
        _album.pattern_accented()
        _album.pattern_numerical()
        _album.pattern_rock_roll()
        return _album.get_string()


class AlbumArtist(object):

    def __init__(self, album_artist):
        self._album_artist = album_artist

    def purge(self):
        self._album_artist = mystrings.Purge(self._album_artist).result()

    def normalize(self):
        _album_artist = Patterns(self._album_artist)
        _album_artist.pattern_featuring()
        _album_artist.pattern_useless_numbers()
        _album_artist.pattern_numerical()
        _album_artist.pattern_rock_roll()
        return _album_artist.get_string()


class Track(AbstractFind):

    PATTERNS = (re.compile("\d{1,2}"),
                re.compile("^\d{2}$"))

    def __init__(self, value):
        super(self.__class__, self).__init__(value, 2)


class Year(AbstractFind):

    PATTERNS = (re.compile("\d{4}"),
                re.compile("^\d{4}$"))

    def __init__(self, value):
        super(self.__class__, self).__init__(value, 4)


class Disc(AbstractFind):

    PATTERNS = (re.compile("\d{1,2}"),
                re.compile("^\d{2}$"))

    def __init__(self, value):
        super(self.__class__, self).__init__(value, 2)


class Genre(object):

    def __init__(self, genre):
        self._genre = genre

    def purge(self):
        pass

    def normalize(self):
        return self._genre


class Comment(object):

    def __init__(self, comment=config.COMMENT):
        self._comment = comment

    def purge(self):
        pass

    def normalize(self):
        return self._comment


class Coded(object):

    PATTERNS = re.compile("^(?:G|RG)$"),

    def __init__(self, coded):
        self._coded = coded

    def purge(self):
        pass

    def normalize(self):
        if self.__class__.PATTERNS[0].match(self._coded):
            return self._coded
        return None


class Normalize(object):

    CLASSES = (Artist,
               Title,
               Album,
               AlbumArtist,
               Track,
               Year,
               Disc,
               Genre,
               Comment,
               Coded)

    def __init__(self, *values):
        self._values = list(values)

    def artist(self, cls, index):
        if self._values[index] and self._values[index + 1]:
            _obj = cls(self._values[index], self._values[index + 1])
            _obj.purge()
            self._values[index], self._values[index + 1] = _obj.normalize()

    def comment(self):
        self._values[Normalize.CLASSES.index(Comment)] = Comment().normalize()

    def others(self, cls, index):
        if self._values[index]:
            _obj = cls(self._values[index])
            _obj.purge()
            self._values[index] = _obj.normalize()

    def normalize(self):
        for _index, _cls in enumerate(Normalize.CLASSES):
            if _cls == Artist:
                self.artist(_cls, _index)
            elif _cls == Comment:
                self.comment()
            else:
                self.others(_cls, _index)
        return self._values


class FileBanner:

    PATTERN = re.compile("(\[[A-Z]{3}\]|)([^-]*)-([^-]*)-(\d{4})(\.\w*)$")

    def __init__(self, value):
        self.value = value
        self.file = os.path.basename(value)
        self.dir = os.path.dirname(value)

    def __bool__(self):
        if self.__class__.PATTERN.match(self.file):
            return True
        return False

    def result(self):
        _result = ""
        _match = self.__class__.PATTERN.match(self.file)
        if _match:
            _match = _match.groups()
            if self.dir:
                _result += self.dir + "/"
            if _match[0] == "":
                _result += "[ITA] "
            else:
                _result += _match[0] + " "
            _result += mystrings.Purge(_match[1]).result() + "-"
            _result += mystrings.Purge(_match[2]).result() + "-"
            _result += _match[3]
            _result += _match[4]
            return _result

    def move(self, check=False):
        _destination = self.result()
        if not _destination:
            return False
        if os.path.isfile(self.value) and not os.path.isfile(_destination):
            print(self.value + " => " + _destination)
            check or shutil.move(self.value, _destination)
            return True
        return False


def normalize(fileslist):
    for _keys, _values in fileslist.items():
        fileslist[_keys] = Normalize(*_values).normalize()
    return fileslist


def main():
   _return = 0
   _arg = False
   for _ in (sys.argv[1:]):
       if _ == "--check":
           _arg = True
           continue
       if not FileBanner(_).move(_arg):
           _return = 127
   exit(_return)


if __name__ == "__main__":
    main()
