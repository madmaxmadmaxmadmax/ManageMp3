#!/data/data/com.termux/files/home/env2/bin/python2.7
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

import config
import normalize
import filesname
import mp3
import shutil
import os
import sys
import myfiles


class AChMod(object):
    def __init__(self, filelist):
        self._filelist = filelist

    @staticmethod
    def chmod(filename):
        if myfiles.ChMod(filename).my_chmod():
            print("Change Mode to File: {}".format(filename))

    def make(self):
        map(self.chmod, self._filelist)


class Directory(object):
    def __init__(self, filename):
        self._filename = filename
        self._path = os.path.dirname(self._filename)

    def exist(self):
        return os.path.exists(self._path)

    def make(self):
        if not self.exist():
            os.makedirs(self._path, config.MODE_DIR)
            print("Make Path {} with mode {}".format(self._path, config.MODE_DIR))


class MoveFile(object):
    def __init__(self, source, destination):
        self._source = source
        self._destination = destination

    def exist(self):
        return os.path.isfile(self._destination)

    def make(self):
        if not self.exist():
            shutil.move(self._source, self._destination)
            print("Move File: {}\nTo: {}".format(self._source, self._destination))
        else:
            print("Skipped File, destination exist: {}".format(self._source))


class RemoveDirs(object):
    def __init__(self, path):
        self._path = path
        self._pathlist = sorted(myfiles.FindDirectories(self._path), reverse=True)

    @staticmethod
    def remove_path(directory):
        if not os.listdir(directory):
            os.rmdir(directory)
            print("Remove Path {}".format(directory))

    def make(self):
        map(self.remove_path, self._pathlist)


class Bone(object):
    def __init__(self, path, ext=config.EXT):
        self._path = path
        self._ext = ext

    def filelist(self):
        return myfiles.FindFiles(self._path, pattern=self._ext)


class APurge(object):
    def __init__(self, path, ext=config.EXT):
        self._path = path
        self._ext = ext
        self._filelist = self.filelist()

    def purge(self):
        AChMod(self._filelist).make()
        for _ in self._filelist:
            _dictionary = mp3.load_tag_mp3(_)
            _dictionary = normalize.normalize(_dictionary)
            mp3.delete_tag_mp3(_)
            mp3.save_tag_mp3(_dictionary)
            print("Purge file: {}".format(_))

    def filelist(self):
        return myfiles.FindFiles(self._path, pattern=self._ext)


class Archive(APurge):
    def __init__(self, path, root, mode):
        super(Archive, self).__init__(path)
        self._root = root
        self._mode = mode

    def archive(self):
        AChMod(self._filelist).make()
        _dictionary = mp3.load_tag_mp3(self._filelist)
        _dictionary = filesname.filesname(_dictionary, self._root, self._mode)
        for _source, _destination in _dictionary:
            Directory(_destination).make()
            MoveFile(_source, _destination).make()
        RemoveDirs(self._path).make()


def purge(path):
    APurge(path).purge()


def archive(path, root=config.ARCHIVE, mode=config.MODE_FILES):
    Archive(path, root, mode).archive()
