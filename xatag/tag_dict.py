import sys
from collections import defaultdict

from xatag.helpers import listify
from xatag.tag import format_tag_value

def tag_list_to_dict(tags):
    """Convert a list of Tags to a dict, where values are lists of strings."""
    try:
        k = tags.keys()
        return tags
    except:
        tags = listify(tags)
        tag_dict = defaultdict(list)
        for t in tags:
            tag_dict[t.key].append(t.value)
        return tag_dict

def print_tag_dict(tag_dict, prefix='', fsep=':', ksep=':', vsep=' ', 
                   one_line=False, key_val_pairs=False, out=None):
    """Print the tags for a file in a nice way."""

    # We need 'out' to be set to the current value of sys.stdout, in case
    # stdout is captured for tests or something.  So we can't say
    # "out=sys.stdout" above.
    if not out: out = sys.stdout

    def write_tag(key_name, dict_key, last_tag=False):
        padding = max(1, longest_tag - len(key_name) + 1)
        sorted_vals = sorted(tag_dict[dict_key])
        do_quote_vals = (vsep==' ')
        formatted_vals = map((lambda x: format_tag_value(x, do_quote_vals)), 
                             sorted_vals)
        if key_val_pairs:
            if one_line: 
                for val in formatted_vals[0:-1]:
                    out.write(key_name + ksep + val + vsep)
                val = formatted_vals[-1]
                out.write(key_name + ksep + val)
                if not last_tag: out.write(vsep)
            else:
                for val in formatted_vals:
                    out.write(prefix + key_name + ksep
                              + " "*padding + val + "\n")
        else:
            if one_line:
                out.write(key_name + ksep)
                out.write('"' + vsep.join(formatted_vals) + '" ')
            else:
                out.write(prefix + key_name + ksep + " "*padding)
                out.write(vsep.join(formatted_vals))
                out.write("\n")
        
    # TODO: compute this using the known tag list, or the tags passed on the
    # command line
    longest_tag = 8     

    if one_line and tag_dict and prefix: 
        out.write(prefix)
    keys = [k for k in sorted(tag_dict.keys())
            if k != '']
    if '' in tag_dict: 
        keys = [''] + keys
    for ind, k in enumerate(keys):
        last_tag = (ind==len(keys)-1)
        if k == '':
            write_tag('tags', '', last_tag=last_tag)
        else:
            write_tag(k, k, last_tag=last_tag)
        
    if one_line and tag_dict and prefix: out.write("\n")
    if (not tag_dict) and prefix:
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
    for k, vlist in minuend.items():
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
    for k, vlist in selection.items():
        if k in original:
            if '' in vlist:
                subset[k] = original[k]
            else:
                new_vlist = [v for v in vlist if v in original[k]]
                if len(new_vlist) > 0: 
                    subset[k] = new_vlist
    return subset

