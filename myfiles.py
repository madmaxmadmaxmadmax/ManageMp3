#!/data/data/com.termux/files/home/env2/bin/python
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

MODE_FILE = 0644


class FilesException(Exception):
    pass


class ChMod:
    def __init__(self, filename):
        self.mode = MODE_FILE
        self.filename = filename

    def get_mode(self):
        return oct(os.stat(self.filename)[0])

    def my_chmod(self):
        if self.get_mode() != "0100{:o}".format(self.mode):
            os.chmod(self.filename, self.mode)
            return True


class Find(object):
    def __init__(self, path, pattern=""):
        self.path = path
        self.pattern = pattern

    def path(self):
        return self.path

    def __iter__(self):
        pass

    def __len__(self):
        return sum(1 for _ in self.__iter__())

    def __getitem__(self, key):
        if isinstance(key, slice):
            return itertools.islice(self, key.start, key.stop)
        else:
            return itertools.islice(self, key, key + 1)


class FindDirectories(Find):
    def __init__(self, path, pattern=""):
        super(FindDirectories, self).__init__(path, pattern)

    def __iter__(self):
        return (_dir_path for _dir_path, _dir_names, _filenames in os.walk(self.path)
                if _dir_path.endswith(self.pattern))


class FindFiles(Find):
    def __init__(self, path, pattern):
        super(FindFiles, self).__init__(path, pattern)

    def __nonzero__(self):
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
