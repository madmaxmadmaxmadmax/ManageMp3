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
          (mutagen.id3.COMM, "COMM::XXX"),
          (mutagen.id3.TXXX, "TXXX:"))


class Mp3Exception(Exception):
    pass


class TagFile:
    def __init__(self, filename):
        self.filename = filename


class TagMP3(TagFile):
    def __init__(self, filename):
        super().__init__(filename)
        self._mp3 = mutagen.mp3.MP3(self.filename)

    @property
    def bitrate(self):
        return f"{self._mp3.info.bitrate / 1000} kb/s"

    @property
    def time(self):
        _time = int(self._mp3.info.length)
        return str(datetime.timedelta(seconds=_time))

    @property
    def seconds(self):
        return int(self._mp3.info.length)

    @property
    def samplerate(self):
        return f"{self._mp3.info.sample_rate} Hz"

    @property
    def layer(self):
        return f"Layer {self._mp3.info.layer}"

    @property
    def mode(self):
        return f"MPEG {self._mp3.info.mode}"


class TagID3(TagFile):
    def __init__(self, filename, encoding=3):
        super().__init__(filename)
        self.encoding = encoding
        try:
            self._id3 = mutagen.id3.ID3(self.filename)
        except mutagen.id3.ID3NoHeaderError:
            self._id3 = mutagen.id3.ID3()

    def __attributeget(self, index):
        try:
            return self._id3.get(LABELS[index][1]).text[0]
        except (AttributeError, IndexError):
            return None

    def __attributeset(self, value, index):
        if value is None:
            return False
        if index == 8:
            self._id3[LABELS[index][1]] = LABELS[index][0](self.encoding, 'XXX', '', value)
        elif index == 9:
            self._id3[LABELS[index][1]] = LABELS[index][0](self.encoding, '', value)
        else:
            self._id3[LABELS[index][1]] = LABELS[index][0](self.encoding, value)
        return True

    def __len__(self):
        return len(LABELS)

    def __str__(self):
        return self._id3.pprint()

    @property
    def artist(self):
        return self.__attributeget(0)

    @artist.setter
    def artist(self, value):
        self.__attributeset(value, 0)

    @property
    def title(self):
        return self.__attributeget(1)

    @title.setter
    def title(self, value):
        self.__attributeset(value, 1)

    @property
    def album(self):
        return self.__attributeget(2)

    @album.setter
    def album(self, value):
        self.__attributeset(value, 2)

    @property
    def albumartist(self):
        return self.__attributeget(3)

    @albumartist.setter
    def albumartist(self, value):
        self.__attributeset(value, 3)

    @property
    def track(self):
        return self.__attributeget(4)

    @track.setter
    def track(self, value):
        self.__attributeset(value, 4)

    @property
    def date(self):
        return self.__attributeget(5)

    @date.setter
    def date(self, value):
        self.__attributeset(value, 5)

    @property
    def disc(self):
        return self.__attributeget(6)

    @disc.setter
    def disc(self, value):
        self.__attributeset(value, 6)

    @property
    def genre(self):
        return self.__attributeget(7)

    @genre.setter
    def genre(self):
        self.__attributeset(value, 7)

    @property
    def comment(self):
        return self.__attributeget(8)

    @comment.setter
    def comment(self, value):
        self.__attributeset(value, 8)

    @property
    def coded(self):
        return self.__attributeget(9)

    @coded.setter
    def coded(self, value):
        self.__attributeset(value, 9)

    def load(self):
        yield self.filename
        yield from (self._TagID3__attributeget(_index) for _index in range(len(self)))

    def delete(self):
        self._id3 and self._id3.delete(self.filename)

    def data(self, values):
        for _index, _value in enumerate(values):
            self.__attributeset(_value, _index)

    def save(self):
        if not os.access(self.filename, os.W_OK):
            raise Mp3Exception(f"File {self.filename} Don't Have Write Permissions")
        self._id3.save(self.filename)


class Abstract:
    def __init__(self, filename, encoding):
        self._filename = filename
        self._encoding = encoding
        try:
            self._id3 = mutagen.id3.ID3(self._filename)
            self._mp3 = mutagen.mp3.MP3(self._filename)
        except mutagen.id3.ID3NoHeaderError:
            self.__header()

    def __header(self):
        self._id3 = mutagen.id3.ID3()
        self._mp3 = mutagen.mp3.MP3()
        self._id3.save(self._filename)

    def __bool__(self):
        if self._id3 and self._mp3:
            return True

    def __attributeget(self, index):
        _value=self._id3.get(LABELS[index][1])
        return _value and str(_value.text[0])

    def __attributeset(self, value, index):
        if index == 8:
            self._id3[LABELS[index][1]] = LABELS[index][0](self._encoding, 'XXX', '', value)
        elif index == 9:
            self._id3[LABELS[index][1]] = LABELS[index][0](self._encoding, '', value)
        else:
            self._id3[LABELS[index][1]] = LABELS[index][0](self._encoding, value)
        self._id3.save(self._filename)

    def __range(self):
        return range(len(LABELS))


class TagMp3(Abstract):
    def __init__(self, filename, encoding=config.ENCODING):
        super().__init__(filename, encoding)
        self._tags = {}
        self._settings = {}

    def load(self):
        _data = [self._Abstract__attributeget(_index) for _index in self._Abstract__range()]
        self._tags = {self._filename: _data}
        return self._tags

    def loaditer(self):
        yield self._filename
        yield from (self._Abstract__attributeget(_index) for _index in self._Abstract__range())

    def save(self, values):
        if not os.access(self._filename, os.W_OK):
            raise Mp3Exception(f"File {self._filename} Don't Have Write Permissions")
        for _index, _value in enumerate(values):
            _value and self._Abstract__attributeset(_value, _index)
        self._id3.save(self._filename)

    def settings(self):
        if self._mp3:
            yield self._filename
            yield from (self.mode, self.layer, self.bitrate, self.samplerate, self.time)

    def delete(self):
        self._id3 and self._id3.delete(self._filename)
        self._mp3 and self._mp3.delete(self._filename)

    def values(self):
        if self._tags:
            return list(self._tags.values())[0]
        else:
            return None

    @property
    def artist(self):
        return self.__attributeget(0)

    @artist.setter
    def artist(self, value):
        self.__attributeset(value, 0)

    @property
    def title(self):
        return self.__attributeget(1)

    @title.setter
    def title(self, value):
        self.__attributeset(value, 1)

    @property
    def album(self):
        return self.__attributeget(2)

    @album.setter
    def album(self, value):
        self.__attributeset(value, 2)

    @property
    def albumartist(self):
        return self.__attributeget(3)

    @albumartist.setter
    def albumartist(self, value):
        self.__attributeset(value, 3)

    @property
    def track(self):
        return self.__attributeget(4)

    @track.setter
    def track(self, value):
        self.__attributeset(value, 4)

    @property
    def date(self):
        return self.__attributeget(5)

    @date.setter
    def date(self, value):
        self.__attributeset(value, 5)

    @property
    def disc(self):
        return self.__attributeget(6)

    @disc.setter
    def disc(self, value):
        self.__attributeset(value, 6)

    @property
    def genre(self):
        return self.__attributeget(7)

    @genre.setter
    def genre(self):
        self.__attributeset(value, 7)

    @property
    def comment(self):
        return self.__attributeget(8)

    @comment.setter
    def comment(self, value):
        self.__attributeset(value, 8)

    @property
    def coded(self):
        return self.__attributeget(9)

    @comment.setter
    def coded(self, value):
        self.__attributeset(value, 9)

    @property
    def bitrate(self):
        return "{} kb/s".format(self._mp3.info.bitrate / 1000)

    @property
    def time(self):
        _time = int(self._mp3.info.length)
        return str(datetime.timedelta(seconds=_time))

    @property
    def seconds(self):
        return int(self._mp3.info.length)

    @property
    def samplerate(self):
        return "{} Hz".format(self._mp3.info.sample_rate)

    @property
    def layer(self):
        return "Layer {}".format(self._mp3.info.layer)

    @property
    def mode(self):
        return "MPEG {}".format(self._mp3.info.mode)


class TagMp3File:
    def __init__(self, arg):
        if isinstance(arg, str):
            self.filelist = arg,
        else:
            self.filelist = arg

    def loadtag(self):
        for _file in self.filelist:
            yield TagMp3(_file).loaditer()

    def load_tag_mp3(self):
        _filelist = {}
        for _ in self.filelist:
            _filelist.update(TagMp3(_).load())
        return _filelist

    def load_settings_mp3(self):
        for _ in self.filelist:
            yield TagMp3(_).settings()

    def delete_tag_mp3(self):
        for _ in self.filelist:
            TagMp3(_).delete()


    def save_tag_mp3(self):
        for _ in self.filelist.items():
            _tag_mp3 = TagMp3(_[0])
            _tag_mp3.save(_[1])


def normalized(filelist, value):
    _data = (None, None, None, None, None,
             None, None, None, None, value)
    for _file in filelist, :
        _tag = TagID3(_file)
        _tag.data(_data)
        _tag.save()


def main():
    for _ in (sys.argv[1:]):
        #normalized(_, "RN")
        print(list(TagID3(_).load()))


if __name__ == "__main__":
    main()
