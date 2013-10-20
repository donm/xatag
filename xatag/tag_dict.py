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


import sys
from collections import defaultdict

from xatag.helpers import listify
from xatag.tag import format_tag_value
import xatag.constants as constants
import xatag.localrecoll as lrcl

def tag_list_to_dict(tags):
    """Convert a list of Tags to a dict, where values are lists of strings."""
    try:
        tags.keys()
        return tags
    except AttributeError:
        tags = listify(tags)
        tag_dict = defaultdict(list)
        for tag in tags:
            tag_dict[tag.key].append(tag.value)
        return tag_dict


def print_tag_dict(tag_dict, prefix='', ksep=':', vsep=' ',
                   one_line=False, key_val_pairs=False,
                   tag_prefix=None, for_recoll=False,
                   terse=False, out=None):
    """Print the tags for a file in a nice way.

    If for_recoll is True, then most of the options will be overwritten;
    tag_prefix can still be altered, though.
    """

    # We need 'out' to be set to the current value of sys.stdout, in case
    # stdout is captured for tests or something.  So we can't say
    # "out=sys.stdout" above.
    if not out:
        out = sys.stdout

    if for_recoll:
        ksep = "="
        vsep = '; '
        one_line = False
        key_val_pair = False
        tag_prefix = None

    if tag_prefix is None:
        tag_prefix = ''

    def write_tag(key_name, dict_key, last_tag=False):
        """Print a single tag formatted properly."""
        padding = max(1, longest_tag - len(key_name) + 1)
        sorted_vals = sorted(tag_dict[dict_key])
        do_quote_vals = (vsep == ' ')
        formatted_vals = [format_tag_value(x, do_quote_vals)
                          for x in sorted_vals]
        if key_val_pairs:
            if one_line:
                for val in formatted_vals[0:-1]:
                    out.write(key_name + ksep + val + vsep)
                val = formatted_vals[-1]
                out.write(key_name + ksep + val)
                if not last_tag:
                    out.write(vsep)
            else:
                for val in formatted_vals:
                    out.write(prefix + key_name + ksep
                              + (" " * padding) + val + "\n")
        else:
            if one_line:
                out.write(key_name + ksep)
                out.write('"' + vsep.join(formatted_vals) + '" ')
            else:
                out.write(prefix + key_name + ksep + (" " * padding))
                # if for_recoll:
                #     out.write('"')
                out.write(vsep.join(formatted_vals))
                # if for_recoll:
                #     out.write('"')
                out.write("\n")

    # TODO: compute this using the known tag list, or the tags passed on the
    # command line
    longest_tag = 8

    if one_line and tag_dict and prefix:
        out.write(prefix)
    keys = sorted(tag_dict.keys())
    default = constants.DEFAULT_TAG_KEY
    if default in keys:
        keys.remove(default)
        keys = [default] + keys
    for ind, k in enumerate(keys):
        last_tag = (ind == len(keys) - 1)
        if for_recoll:
            keyname = lrcl.tag_key_to_recoll_prefix(k)
        else:
            keyname = tag_prefix + k
        write_tag(keyname, k, last_tag=last_tag)

    if one_line and tag_dict and prefix:
        out.write("\n")
    # Show that the file doesn't have the requested tags.
    if (not tag_dict) and prefix and not terse:
        out.write(prefix + "\n")


def merge_tags(tags1, tags2):
    """Merge the two tag dicts."""
    combined = {}
    for k in tags1.keys():
        if k in tags2.keys():
            combined[k] = tags2[k] + [v for v in tags1[k]
                                      if v not in set(tags2[k])]
        else:
            combined[k] = tags1[k]
    for key in [k for k in tags2.keys() if k not in tags1.keys()]:
        combined[key] = tags2[key]
    return combined


# For these next two functions, the second argument can be a tag dict from a
# file, but it can also have tags with empty values, which means "all tags
# with this key."

def subtract_tags(minuend, subtrahend, empty_means_all=True):
    """Return the tag values in minuend with those in subtrahend removed.

    If subtrahend has a key with a value of '' in its list, then that will
    remove all tag values from minuend from the same key.
    """
    difference = {}
    for k, vlist in minuend.items():
        if k in subtrahend.keys():
            if '' in subtrahend[k] and empty_means_all:
                pass
            else:
                new_vlist = [v for v in vlist
                             if v not in subtrahend[k]]
                if len(new_vlist) > 0:
                    difference[k] = new_vlist
        else:
            difference[k] = vlist
    return difference


def select_tags(original, selection):
    """Return the tags in original that are also in selection.

    If selection has a key with a value of '' in its list, then that will
    select all tag values from original from the same key.

    """
    subset = {}
    for k, vlist in selection.items():
        if k in original:
            if '' in vlist:
                subset[k] = original[k]
            else:
                new_vlist = [v for v in vlist if v in original[k]]
                if len(new_vlist) > 0:
                    subset[k] = new_vlist
    return subset
