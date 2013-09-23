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

def print_tag_dict(tag_dict, prefix='', fsep=':', ksep=':', tsep=' ', 
                   one_line=False, key_val_pairs=False, out=sys.stdout):
    """Print the tags for a file in a nice way."""
    def write_tag(key_name, dict_key):
        padding = max(1, longest_tag - len(key_name) + 1)
        sorted_vals = sorted(tag_dict[dict_key])
        if (key_val_pairs and one_line):
            do_quote_vals = False 
        else:
            do_quote_vals = (tsep==' ')
        formatted_vals = map((lambda x: format_tag_value(x, do_quote_vals)), 
                             sorted_vals)
        if key_val_pairs:
            if one_line: 
                for val in formatted_vals:
                    out.write(key_name + ksep + val + tsep)
            else:
                for val in formatted_vals:
                    out.write(prefix + key_name + ksep + " "*padding + val + "\n")
        else:
            if one_line:
                out.write(key_name + ksep)
                out.write('"' + tsep.join(formatted_vals) + '" ')
            else:
                out.write(prefix + key_name + ksep + " "*padding)
                out.write(tsep.join(formatted_vals))
                out.write("\n")
        
    # TODO: compute this using the known tag list, or the tags passed on the
    # command line
    longest_tag = 8     

    if one_line and tag_dict and prefix: out.write(prefix)
    if '' in tag_dict:
        write_tag('tags', '')
    for k in sorted(tag_dict.keys()):
        if k=='' or k=='tags': continue
        write_tag(k, k)
    if one_line and tag_dict and prefix: out.write("\n")
    if (not tag_dict) and prefix:
        out.write(prefix + "\n")

def print_file_tags(fname, longest_filename=0, fsep=":", ksep=':', tsep=' ', 
                    one_line=False, key_val_pairs=False, 
                    out=sys.stdout, **unused):
    padding = max(1, longest_filename - len(fname) + 1)
    prefix = fname + fsep + " "*padding
    print_tag_dict(read_tags_as_dict(fname), prefix=prefix, fsep=fsep, ksep=ksep, tsep=tsep, 
                   one_line=one_line, key_val_pairs=key_val_pairs, out=out)

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

