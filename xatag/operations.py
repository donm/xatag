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
import os
import xattr
import subprocess
# from recoll import recoll

import xatag.tag_dict as xtd
import xatag.attributes as attr
from xatag.tag import Tag
from xatag.warn import warn
import xatag.config as config

# Some functions below have the argument '**unused'.  That's to facilitate
# passing the options array that is returned from docopt (after some fixing)
# to the function.  The docopt option array has many options that each
# function doesn't need to accept as a keyword, so the extras are accepted and
# not used.

# It's kind of a hack, but consider the alternatives.  Either:
#
# * Check for optional keyword arguments in every caller just to pass them on.
#   That's unneccesary, boring code and tighter coupling.
#
# * Have these functions accept a dictionary of optional arguments, instead of
#   accepting only the arguments they need as keywords.  This is less
#   transparent when reading the code and deciding which options are
#   available, plus it's a step away from functional style.
#
# If you see a better alternatives, let me know.

# Why don't add_tags, delete_tags, etc. use the merge_tags, subtract_tags, and
# select_tags function?  Only because those require a passing a full dict of
# all tags, and I don't want to have to read and parse the extended attributes
# of fields that we know won't change.  Whether that speeds things up or not
# right now, I don't know, but it could with future changes in either this
# program or in the xattr package.


def add_tags(fname, tags, **unused):
    """Add the given tags from the xatag managed xattr fields of fname."""
    tags = xtd.tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for key, value_list in tags.items():
        values_to_add = []
        for v in value_list:
            if v == '':
                warn("tag is missing value: " + Tag(key, v).to_string())
            else:
                values_to_add.append(v)
        if len(values_to_add) != 0:
            xattr_key = attr.xatag_to_xattr_key(key)
            if xattr_key in attributes.keys():
                current_field = attributes[xattr_key]
            else:
                current_field = ''
            new_field = attr.add_tag_values_to_xattr_value(current_field,
                                                           values_to_add)
            attributes[xattr_key] = new_field


def set_tags(fname, tags, **unused):
    """Set any key mentioned in tags to the values in tags for that key."""
    tags = xtd.tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for k, v in tags.items():
        xattr_key = attr.xatag_to_xattr_key(k)
        xattr_value = attr.list_to_xattr_value(v)
        if xattr_value == '':
            attributes.remove(xattr_key)
        else:
            attributes[xattr_key] = xattr_value


def set_all_tags(fname, tags, **unused):
    """Set and keep only the keys mentioned, removing all other keys."""
    delete_all_tags(fname)
    set_tags(fname, tags)


def delete_tags(fname, tags, complement=False, quiet=False, **unused):
    """Delete tags from fname.

    A tag with tag.value=='' will delete all tags for that key.

    If complement is true, then delete all tags other than those given.
    """
    if complement:
        return delete_other_tags(fname, tags, quiet=quiet)
    else:
        return delete_these_tags(fname, tags, quiet=quiet)


def delete_these_tags(fname, tags, quiet=False, **unused):
    """Delete the given tags from the xatag managed xattr fields of fname."""
    tags = xtd.tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for k, vlist in tags.items():
        xattr_key = attr.xatag_to_xattr_key(k)
        if xattr_key in attributes:
            if '' in vlist:
                attributes.remove(xattr_key)
            else:
                current_field = attributes[xattr_key]
                new_field = attr.remove_tag_values_from_xattr_value(
                    current_field, vlist)
                # This is important when the user says 'key' but means 'key:'
                if current_field == new_field and not quiet:
                    warn(fname + ": tag key unchanged: " + (k or 'tags'))
                if new_field == '':
                    if not quiet:
                        warn(fname + ": removing empty tag key: " + (k or 'tags'))
                    attributes.remove(xattr_key)
                else:
                    attributes[xattr_key] = new_field
        # elif not quiet:
        #     if k == '':
        #         print("no simple tags not found")
        #     else:
        #         print("key not found: " + k)


def delete_other_tags(fname, tags, quiet=False, out=sys.stdout, **unused):
    """Delete tags other than the given tags from the xatag fields of fname."""
    tags = xtd.tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    # We have to be careful here, because we're iterating over every xattr,
    # not just those in the xatag namespace.
    for xattr_key in attributes.keys():
        if not attr.is_xatag_xattr_key(xattr_key):
            continue
        k = attr.xattr_to_xatag_key(xattr_key)
        if k not in tags.keys():
            attributes.remove(xattr_key)
        else:
            current_field = attributes[xattr_key]
            vlist = tags[k]
            new_field = attr.remove_tag_values_from_xattr_value(
                current_field, vlist, complement=True)
            if new_field == '':
                if not quiet:
                    warn("removing empty tag key:" + (k or 'tags'))
                attributes.remove(xattr_key)
            else:
                attributes[xattr_key] = new_field


def delete_all_tags(fname, **unused):
    """Delete all xatag managed xattr fields of fname."""
    attributes = xattr.xattr(fname)
    for key in attributes:
        if attr.is_xatag_xattr_key(key):
            attributes.remove(key)


def print_file_tags(fname, tags=False, subset=False, complement=False,
                    terse=False, quiet=False,
                    longest_filename=0, fsep=":", ksep=':', vsep=' ',
                    one_line=False, key_val_pairs=False,
                    for_recoll=False, print_filename=True,
                    tag_prefix=None,
                    out=None, **unused):
    # We need 'out' to be set to the current value of sys.stdout, in case
    # stdout is captured for tests or something.  So we can't say
    # "out=sys.stdout" above.
    if not out:
        out = sys.stdout
    # It's a little funny having this check here, but the alternative is
    # having it in every function that calls this one.  Also, maybe in the
    # future quiet will do something else.
    if quiet:
        return

    if for_recoll or not print_filename:
        prefix = ''
    else:
        padding = max(1, longest_filename - len(fname) + 1)
        prefix = fname + fsep + (" " * padding)

    tag_dict = attr.read_tags_as_dict(fname)
    if subset:
        tag_dict = subsetted_tags(tag_dict, tags, complement=complement)
    elif terse:
        tags = xtd.tag_list_to_dict(tags)
        if complement:
            just_tag_keys_dict = {key: '' for key in tag_dict
                                  if key not in tags}
        else:
            just_tag_keys_dict = {key: '' for key in tags}
        tag_dict = subsetted_tags(tag_dict, just_tag_keys_dict,
                                  complement=complement)

    xtd.print_tag_dict(tag_dict, prefix=prefix, ksep=ksep,
                       vsep=vsep, one_line=one_line,
                       key_val_pairs=key_val_pairs,
                       for_recoll=for_recoll, tag_prefix=tag_prefix,
                       out=out)

def subsetted_tags(source_tags, tags=False, complement=False, **unused):
    if tags:
        tags = xtd.tag_list_to_dict(tags)
        if complement:
            source_tags = xtd.subtract_tags(source_tags, tags)
        else:
            source_tags = xtd.select_tags(source_tags, tags)
    return source_tags


def copy_tags(source_tags, destination, tags=False, complement=False,
              **unused):
    """Copy tags in dict souce_tags to each file in destinations."""
    source_tags = subsetted_tags(source_tags, tags, complement=complement)
    new_tags = xtd.merge_tags(source_tags, attr.read_tags_as_dict(destination))
    set_tags(destination, new_tags)


def copy_tags_over(source_tags, destination, tags=False, complement=False,
                   **unused):
    """Copy xatag managed xattr fields, removing all other tags."""
    delete_all_tags(destination)
    copy_tags(source_tags, destination, tags, complement)


def update_recoll_index(files, **other_args):
    """Try to update the recoll index for files."""
    if 'destinations' in other_args:
        files += other_args['destinations']

    # Creating the rclmonixnow file is only necessary if the recollindex call
    # is blocked, meaning that the the Recoll daemon is running. However,
    # recollindex takes a perceptible amount of time, so let's just do both so
    # we can run recollindex in the background and not wait for the exit
    # status.
    try:
        rcl_dir = config.get_recoll_base_config_dir()
        if rcl_dir:
            open(os.path.join(rcl_dir, 'rclmonixnow'), 'w').close()

        # cwd = os.environ.get('PWD')
        # if cwd:
            # files = [os.path.join(cwd, fname) for fname in files]
        with open('/dev/null', 'w') as devnull:
            # Use Popen() instead of call() to run in the background.
            subprocess.Popen(['recollindex', '-i'] + files,
                             stdout=devnull, stderr=devnull)

    except:
        warn("There was a problem updating the Recoll index.")
