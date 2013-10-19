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


import xatag.constants as constants


class Tag:
    """Simple container for tag key/value pairs."""
    def __init__(self, key, value=''):
        if key == '':
            key = constants.DEFAULT_TAG_KEY
        self.key = format_tag_key(key)
        self.value = format_tag_value(value)

    @classmethod
    def from_string(cls, tag_str):
        """Create a list of Tag object from a string.

        Where (k,v) denotes Tag(k,v):
            'multi:part:key:value' -> [('multi:part:key', 'value')]
            'simple-tag' -> [('tags', 'simple-tag')]
            'key:val1;val2;...' -> [('key', 'val1'), ('key', 'val2'), ...]
        """
        parts = tag_str.split(':')
        if len(parts) == 1:
            key = constants.DEFAULT_TAG_KEY
            values = tag_str
        else:
            key = ':'.join(parts[0:-1])
            values = parts[-1]
        return [cls(key, v)
                for v in values.split(constants.XATTR_FIELD_SEPARATOR)]

    def to_string(self):
        """Create a 'key:value' formatted string from a Tag object."""
        if self.key == constants.DEFAULT_TAG_KEY:
            return self.value
        else:
            return self.key + ":" + self.value

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


def format_tag_key(string):
    """Format tag key string when reading or writing to extended attributes."""
    return " ".join(string.strip().split())


# quote when printing, not when reading or writing
def format_tag_value(string, quote=False):
    """Format tag value string when reading or writing to extended attributes.

    When formatting the tag value for printing, set quote=True to quote tags
    with whitespace.

    """
    string = " ".join(string.strip().split())
    if quote:
        string = "'" + string + "'" if ' ' in string else string
    return string
