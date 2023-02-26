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

import optparse
import amain


def main():
    usage = "usage: %prog [options] directory"
    parser = optparse.OptionParser(usage)
    parser.add_option("--purge", help="Purge mp3 tags", action="store_true", dest="purge")
    parser.add_option("--archive", help="Store files in directory", action="store_true", dest="archive")
    parser.add_option("--check", help="Store files in directory", action="store_true", dest="check")
    (options, args) = parser.parse_args()

    if options.purge:
        if len(args) == 1:
            print "Purge {}...".format(args[0])
            amain.purge(args[0])

    if options.archive:
        print "Archive {}...".format(args[0])
        if len(args) == 2:
            print "To {}...".format(args[1])
            amain.archive(args[0], args[1])
        if len(args) == 1:
            amain.archive(args[0])

    if options.check:
        if len(args) == 1:
            print "Check {}...".format(args[0])
            if not amain.check(args[0]):
                exit(1)


if __name__ == "__main__":
    main()
