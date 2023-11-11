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

TAGS = ("Artist",
        "Title",
        "Album",
        "AlbumArtist",
        "Track",
        "Year",
        "Disc",
        "Genre",
        "Comment",
        "Coded")


class Bone:
    def __init__(self, values, mode):
        self._values = values
        self._mode = mode
        self._name = None


class Parser(Bone):
    def __init__(self, values, mode):
        super().__init__(values, mode)
        self._parser = self.parser()

    def parser(self):
        _string = []
        _tag = lambda x: self._values[TAGS.index(x)]
        try:
            for _ in self._mode:
                _string.append("-".join(_tag(__) for __ in _.split("-")))
        except TypeError:
            _string.append("")
        return _string


# noinspection PyUnresolvedReferences
class Purge(object):

    PATTERN = (re.compile("(^.*\({0}|^.*\({1}|^.*\({2}) ([1-9][0-9]|[2-9])\)\.{ext}"
                          .format(*config.TYPES, ext=config.EXT[0])),
               re.compile("(^.*\({1}|^.*\({2})\).{ext}"
                          .format(*config.TYPES, ext=config.EXT[0])))

    def __init__(self, filename):
        self._filename = filename

    def extension(self):
        self._filename += f".{config.EXT[0]}"

    def purge(self):
        if Purge.PATTERN[0].match(self._filename):
            self._filename = Purge.PATTERN[0].sub("\\1", self._filename)
            self._filename += ")"
            self.extension()
        if self._filename.endswith(f"({config.TYPES[0]}).{config.EXT[0]}"):
            self._filename = self._filename[:-14]
            self.extension()
        return self._filename

    def add(self):
        _match1 = Purge.PATTERN[0].match(self._filename)
        _match2 = Purge.PATTERN[1].match(self._filename)
        if _match1:
            _base = _match1.group(1)
            _value = int(_match1.group(2)) + 1
            self._filename = "{} {})".format(_base, _value)
        elif _match2:
            _base = _match2.group(1)
            self._filename = "{} 2)".format(_base)
        else:
            self._filename = "{} ({} 2)".format(self._filename[:-4], config.TYPES[0])
        self.extension()
        return self._filename


class Directory(Parser):

    ARTICLES = ("the ", "i ")

    def __init__(self, values, root, mode):
        super(Directory, self).__init__(values, mode)
        self._root = root

    def articles(self):
        for _article in self.__class__.ARTICLES:
            _len = len(_article)
            if self._parser[0][0:_len].lower() == _article:
                self._parser.insert(0, self._parser[0][_len:_len + 1].upper())
                return True

    def name(self):
        if self._name:
            return self._name
        try:
            if self._parser[0][:1].isdigit():
                self._parser.insert(0, "0..9")
            elif self.articles():
                pass
            else:
                self._parser.insert(0, self._parser[0][:1].upper())
        except IndexError:
            pass
        self._name = "{}/{}".format(self._root, "/".join(self._parser))
        return self._name


class FileName(Parser):
    def __init__(self, values, root, mode_dir, mode_file):
        super(FileName, self).__init__(values, mode_file)
        self._directory = Directory(values, root, mode_dir)

    def name(self):
        if self._name:
            return self._name
        self._name = "{}/{}.{}".format(self._directory.name(), "-".join(self._parser), config.EXT[0])
        return self._name


class CreateList(object):
    def __init__(self, keys, filename, filelist):
        self._keys = keys
        self._filename = filename
        self._filelist = filelist

    def is_present(self):
        _filelist = (destination for source, destination in self._filelist)
        return self._filename in _filelist

    def make(self):
        while True:
            if self.is_present():
                self._filename = Purge(self._filename).add()
            else:
                self._filelist += ((self._keys, self._filename), )
                break
        return self._filelist


def filesname(filelist, root=config.ARCHIVE, xxx_todo_changeme=config.MODE_FILES):
    (mode_dir, mode_files) = xxx_todo_changeme
    _filelist = ()
    for _keys, _values in filelist.items():
        _filename = FileName(_values, root, mode_dir, mode_files).name()
        _filelist = CreateList(_keys, _filename, _filelist).make()
    return _filelist
