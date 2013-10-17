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


import collections


def listify(arg):
    """Make arg iterable, if it's not already.

    I'm sure there's some other iterable object besides a string that you
    would want to listify, but I can't think of them right now.
    """
    if (((not isinstance(arg, collections.Iterable))
         or isinstance(arg, basestring))):
        return [arg]
    else:
        return arg
