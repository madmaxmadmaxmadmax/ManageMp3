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
__version__ = '1.0'
__license__ = 'Public Domain'

import mutagen.id3
import mutagen.mp3
import datetime
import os
import sys
import config


LABELS = ((mutagen.id3.TPE1, "TPE1"),
          (mutagen.id3.TIT2, "TIT2"),
          (mutagen.id3.TALB, "TALB"),
          (mutagen.id3.TPE2, "TPE2"),
          (mutagen.id3.TRCK, "TRCK"),
          (mutagen.id3.TDRC, "TDRC"),
          (mutagen.id3.TPOS, "TPOS"),
          (mutagen.id3.TCON, "TCON"),
          (mutagen.id3.COMM, "COMM::'XXX'"),
          (mutagen.id3.TXXX, "TXXX:"))


class Mp3Exception(Exception):
    pass


# noinspection PyUnresolvedReferences
class TagMp3(object):
    def __init__(self, filename, encoding=config.ENCODING):
        self._filename = filename
        self._encoding = encoding
        self._tags = {}
        self._settings = {}
        try:
            self._id3 = mutagen.id3.ID3(self._filename)
            self._mp3 = mutagen.mp3.MP3(self._filename)
        except mutagen.id3.ID3NoHeaderError:
            self._new()

    def _new(self):
        self._id3 = mutagen.id3.ID3()
        self._mp3 = mutagen.mp3.MP3()
        self._id3.save(self._filename)

    def __nonzero__(self):
        if self._id3 or self._mp3:
            return True

    def load(self):
        _data = [_.text[0].encode(config.CODING)
                 if _ is not None else None for _ in map(self._id3.get, [_[1] for _ in LABELS])]
        self._tags = {self._filename: _data}
        return self._tags

    def save(self, args):
        if not os.access(self._filename, os.W_OK):
            raise Mp3Exception("File {filename} Don't Have Write Permissions".format(filename=self._filename))
        for _ in enumerate(LABELS):
            if args[_[0]]:
                if _[1][1] == "COMM::'XXX'":
                    self._id3[_[1][1]] = _[1][0](self._encoding, 'XXX', '', args[_[0]].decode(config.CODING))
                elif _[1][1] == "TXXX:":
                    self._id3[_[1][1]] = _[1][0](self._encoding, '', args[_[0]].decode(config.CODING))
                else:
                    self._id3[_[1][1]] = _[1][0](self._encoding, args[_[0]].decode(config.CODING))
        self._id3.save(self._filename)

    def settings(self):
        _data = (None, None, None, None, None)
        if self._mp3:
            _data = (self._mode, self._layer, self._bitrate, self._sample_rate, self._time)
        self._settings = {self._filename: _data}
        return self._settings

    def delete(self):
        if self._id3:
            self._id3.delete(self._filename)
        if self._mp3:
            self._mp3.delete(self._filename)

    def values(self):
        if self._tags:
            return self._tags.values()[0]
        else:
            return None

    @property
    def _bitrate(self):
        return "{} kb/s".format(self._mp3.info.bitrate / 1000)

    @property
    def _time(self):
        _time = int(self._mp3.info.length)
        return str(datetime.timedelta(seconds=_time))

    @property
    def _seconds(self):
        return int(self._mp3.info.length)

    @property
    def _sample_rate(self):
        return "{} Hz".format(self._mp3.info.sample_rate)

    @property
    def _layer(self):
        return "Layer {}".format(self._mp3.info.layer)

    @property
    def _mode(self):
        return "MPEG {}".format(self._mp3.info.mode)


def load_tag_mp3(fileslist):
    _fileslist = {}
    if isinstance(fileslist, str):
        fileslist = fileslist,
    for _ in fileslist:
        _fileslist.update(TagMp3(_).load())
        #print("Load tags from file: {}".format(_))
    return _fileslist


def load_settings_mp3(fileslist):
    _fileslist = {}
    if isinstance(fileslist, str):
        fileslist = fileslist,
    for _ in fileslist:
        _fileslist.update(TagMp3(_).settings())
        #print("Load settings from file: {}".format(_))
    return _fileslist


def delete_tag_mp3(fileslist):
    if isinstance(fileslist, str):
        fileslist = fileslist,
    for _ in fileslist:
        TagMp3(_).delete()


def save_tag_mp3(fileslist):
    for _ in fileslist.iteritems():
        _tag_mp3 = TagMp3(_[0])
        _tag_mp3.save(_[1])
        #print("Save tags to file: {}".format(_[0]))


def change_album(filelist, album_type):
    _filelist = load_tag_mp3(filelist)
    for _ in _filelist:
        _filelist[_][2] += album_type
    save_tag_mp3(_filelist)


def main():
   for _ in (sys.argv[1:]):
       print TagMp3(_).load()


if __name__ == "__main__":
    main()
