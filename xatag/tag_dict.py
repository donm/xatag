import xattr
import sys
from collections import defaultdict

from helpers import listify
from attributes import *
from tag import format_tag_value

def read_tags_as_dict(fname):
    """Return a dict of the xattr fields in fname in the xatag namespace."""
    attributes = xattr.xattr(fname)
    # no sense in reading the value if the key isn't going to be chosen
    return {xattr_to_xatag_key(k): xattr_value_to_list(attributes[k])
            for k in attributes if is_xatag_xattr_key(k)}

def tag_list_to_dict(tags):
    """Convert a list of Tags to a dictionary, where the values are lists of strings."""
    try:
        k = tags.keys()
        return tags
    except:
        tags = listify(tags)
        tag_dict = defaultdict(list)
        for t in tags:
            tag_dict[t.key].append(t.value)
        return tag_dict

def print_tag_dict(tag_dict, out=sys.stdout):
    """Print the tags for a file in a nice way."""
    if '' in tag_dict:
        out.write(" ".join(map((lambda x: format_tag_value(x, True)), sorted(tag_dict['']))))
        out.write("\n")
    for k in sorted(tag_dict.keys()):
        if k=='' or k=='tags': continue
        out.write(k + ': ')
        out.write(" ".join(map((lambda x: format_tag_value(x, True)), sorted(tag_dict[k]))))
        out.write("\n")

def print_file_tags(fname, out=sys.stdout):
    print_tag_dict(read_tags_as_dict(fname), out=out)

def merge_tags(tags1, tags2):
    """Merge the two tag dicts."""
    combined = {}
    for k in tags1.keys():
        if k in tags2.keys():
            combined[k] = tags2[k] + [v for v in tags1[k] 
                                      if v not in set(tags2[k])]
        else:
            combined[k] = tags1[k]
    for k in [k for k in tags2.keys() if k not in tags1.keys()]:
        combined[k] = tags2[k]        
    return combined

# For these next two functions, the second argument can be a tag dict from a
# file, but it can also have tags with empty values, which means "all tags
# with this key."

def subtract_tags(minuend, subtrahend):
    """Remove the tag values in subtrahend from minuend.
    
    If subtrahend has a key with a value of '' in its list, then that will
    remove all tag values from minuend from the same key.
    """
    difference = {}
    for k,vlist in minuend.items():
        if k in subtrahend.keys():
            if '' in subtrahend[k]:
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
    for k,vlist in selection.items():
        if k in original:
            if '' in vlist:
                subset[k] = original[k]
            else:
                new_vlist = [v for v in vlist if v in original[k]]
                if len(new_vlist) > 0: 
                    subset[k] = new_vlist
    return subset

