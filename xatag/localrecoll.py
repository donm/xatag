# Copyright (c) 2013 Don March <don@ohspite.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import string

import xatag.constants as constants


def tag_key_to_recoll_prefix(key):
    key = str(key)
    to_sub = string.punctuation + string.whitespace
    table = string.maketrans(to_sub, ':' * len(to_sub))
    return (constants.RECOLL_TAG_PREFIX + key.translate(table))


def tag_key_to_xapian_key(key):
    table = string.maketrans('', '')
    return (constants.RECOLL_XAPIAN_PREFIX +
            key.upper().translate(table,
                                  string.punctuation + string.whitespace))
