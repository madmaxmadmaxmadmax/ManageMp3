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
__version__ = '0.1'
__license__ = 'Public Domain'

import itertools
import os
import shutil

MODEFILE = 0o644
MODEDIR = 0o700


class FileException(Exception):
    pass


class Abstract:
    def __new__(cls, *args, **kwargs):
        _obj = super().__new__(cls)
        cls.__init__(_obj, *args, **kwargs)
        return _obj.make()

    def make(self):
        pass


class ChMod(Abstract):
    def __init__(self, value):
        if isinstance(value, str):
            self.value = (value, )
        else:
            self.value = value

    @staticmethod
    def mode(file):
        return oct(os.stat(file)[0])

    def make(self):
        for _file in self.value:
            if self.mode(_file) != "0100{:o}".format(MODEFILE):
                os.chmod(_file, MODEFILE)


class MoveFile(Abstract):
    def __init__(self, *args):
        self.source = args[0]
        self.destination = args[1]

    def make(self):
        if os.path.isfile(self.source) and not os.path.isfile(self.destination):
            shutil.move(self.source, self.destination)
            return True
        return False


class MoveFiles(Abstract):
    def __init__(self, generators):
        self.generators = generators

    def make(self):
        for _generator in self.generators:
            for _source, _destination in _generator:
                if MoveFile(_source, _destination):
                    _sep = "=>"
                else:
                    _sep = "=="
                print(f"{_source} {_sep} {_destination}")


class MakeDir(Abstract):
    def __init__(self, value):
        self.path = os.path.dirname(value)

    def make(self):
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path, MODEDIR)
                return True
            except PermissionError:
                pass
        return False


class MakeDirs(Abstract):
    def __init__(self, generator):
        self.generator = generator

    def make(self):
        for _dir in self.generator:
            if MakeDir(_dir):
                print(f" => {_dir}")


class RemoveDirs(Abstract):
    def __init__(self, path):
        self.dirs = sorted(FindDirectories(path), reverse=True)

    @staticmethod
    def remove_path(directory):
        if not os.listdir(directory):
            os.rmdir(directory)
            return True
        return False

    def make(self):
        list(map(self.remove_path, self.dirs))


class OLDRemoveDirs(Abstract):
    def __init__(self, path):
        self.dirs = FindDirectories(path)

    def make(self):
        for _dir in self.dirs:
            try:
                os.rmdir(_dir)
            except OSError:
                pass


class Find:

    def __init__(self, path, pattern):
        self.path = os.path.abspath(path)
        self.pattern = pattern

    def __iter__(self):
        pass

    def __len__(self):
        return sum(1 for _ in self.__iter__())

    def __getitem__(self, key):
        if isinstance(key, slice):
            return itertools.islice(self, key.start, key.stop)
        return itertools.islice(self, key, key + 1)


class FindDirectories(Find):

    def __init__(self, path, pattern=""):
        super().__init__(path, pattern)

    def __iter__(self):
        for _dir_path, _dir_names, _filenames in os.walk(self.path):
            if _dir_path.endswith(self.pattern):
                yield _dir_path


class FindFiles(Find):

    def __init__(self, path, pattern=""):
        super().__init__(path, pattern)

    def __bool__(self):
        for _dir_path, _dir_names, _filenames in os.walk(self.path):
            for _filename in _filenames:
                if _filename.endswith(self.pattern):
                    return True
        return False

    def __iter__(self):
        for _dir_path, _dir_names, _filenames in os.walk(self.path):
            for _filename in _filenames:
                if _filename.endswith(self.pattern):
                    yield os.path.join(_dir_path, _filename)


class FirstChar(Abstract):

    PATTERNS = ("the", "i")

    def __init__(self, value):
        try:
            self.value = value.lower()
        except AttributeError:
            self.value = None

    def firstchar(self):
        _index = 0
        while True:
            _first = self.value[_index]
            match _first:
                case _first.isnumeric():
                    return "0..9"
                case "à":
                    return "A"
                case "è":
                    return "E"
                case "ì":
                    return "I"
                case "ò":
                    return "O"
                case "ù":
                    return "U"
                case _first.isalpha():
                    return _first.upper()
            _index += 1

    def make(self):
        if not self.value:
            return None
        for _pattern in self.__class__.PATTERNS:
            _pattern += " "
            if self.value.startswith(_pattern):
                self.value = self.value.strip(_pattern)
        return self.firstchar()


class Join(Abstract):

    def __init__(self, *args, sep):
        self.sep = sep
        args = [_args for _args in args if _args]
        if len(args) == 0 and  isinstance(args, list):
            self.args = ""
        elif isinstance(args, str):
            self.args = (args, )
        else:
            self.args = args

    def make(self):
        return self.sep.join(self.args)


class FileName(Abstract):

    def __init__(self, root, generator):
        self.root = os.path.abspath(root)
        self.generator = generator

    def make(self):
        yield next(self.generator)
        _tags = tuple(self.generator)
        _firstchar = FirstChar(_tags[3])
        _album = Join(_tags[5], _tags[2], sep="-")
        _filename = Join(_tags[4], _tags[0], _tags[1], sep="-")
        _filename = Join(self.root, _firstchar, _tags[3], _album, _tags[6], _filename, sep="/")
        yield f"{_filename}.mp3"
