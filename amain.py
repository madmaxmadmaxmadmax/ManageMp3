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

import mp3
import files
import config
import normalize
import filesname


class Bone:
    def __init__(self, path, ext):
        self.path = path
        self.ext = ext
        self.filelist = files.FindFiles(self.path, pattern=self.ext)


class Purge(Bone):
    def __init__(self, path, ext):
        super().__init__(path, ext)

    def purge(self):
        files.ChMod(self.filelist)
        for _file in self.filelist:
            _dictionary = mp3.TagMp3File(_file).load_tag_mp3()
            _dictionary = normalize.normalize(_dictionary)
            mp3.TagMp3File(_file).delete_tag_mp3()
            mp3.TagMp3File(_dictionary).save_tag_mp3()
            print(f" => {_file}")


class Archive(Purge):
    def __init__(self, path, ext, root, mode):
        super().__init__(path, ext)
        self._root = root
        self._mode = mode

    def archive(self):
        files.ChMod(self.filelist)
        _dictionary = mp3.TagMp3File(self.filelist).load_tag_mp3()
        _dictionary = filesname.filesname(_dictionary, self._root, self._mode)
        for _source, _destination in _dictionary:
            files.MakeDir(_destination)
            if files.MoveFile(_source, _destination):
                print(f"{_source} => {_destination}")
        files.RemoveDirs(self.path)


def purge(path, ext=config.EXT):
    Purge(path, ext).purge()


def archive(path, ext=config.EXT, root=config.ARCHIVE, mode=config.MODE_FILES):
    Archive(path, ext, root, mode).archive()


def check(path, ext=config.EXT):
    if files.FindFiles(path, ext):
        return True
    return False
