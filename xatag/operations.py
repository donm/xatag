import sys
import xattr
import os
from collections import defaultdict
from recoll import recoll

from helpers import listify
from tag_dict import *
from attributes import *
from tag import *
from warn import warn

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
    tags = tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for key, value_list in tags.items():
        values_to_add = []
        for v in value_list:
            if v == '':
                warn("tag is missing value: " + Tag(key,v).to_string())
            else: 
                values_to_add.append(v)
        if len(values_to_add) != 0:
            xattr_key = xatag_to_xattr_key(key)
            if xattr_key in attributes.keys():
                current_field = attributes[xattr_key]
            else:
                current_field = ''
            new_field = add_tag_values_to_xattr_value(current_field, values_to_add)
            attributes[xattr_key] = new_field
   
def set_tags(fname, tags, **unused):
    """Set any key mentioned in tags to the values in tags for that key."""
    tags = tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for k,v in tags.items():
        xattr_key = xatag_to_xattr_key(k)
        xattr_value = list_to_xattr_value(v)
        if xattr_value == '':
            attributes.remove(xattr_key)
        else:
            attributes[xattr_key] = xattr_value

def set_all_tags(fname, tags, **unused):
     """Set and keep only the keys mentioned in tags, removing all other keys."""
     delete_all_tags(fname)
     set_tags(fname, tags)

def delete_tags(fname, tags, complement=False, quiet=False, **unused):
    if complement:
        return delete_other_tags(fname, tags, quiet=quiet)
    else:
        return delete_these_tags(fname, tags, quiet=quiet)

def delete_these_tags(fname, tags, quiet=False, **unused):
    """Delete the given tags from the xatag managed xattr fields of fname."""
    tags = tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for k,vlist in tags.items():
        xattr_key = xatag_to_xattr_key(k)
        if xattr_key in attributes: 
            if '' in vlist:
                attributes.remove(xattr_key)
            else:
                current_field = attributes[xattr_key]
                new_field = remove_tag_values_from_xattr_value(current_field, vlist)
                if new_field == '': 
                    if not quiet: warn(fname + ": removing empty tag key: " + k)
                    attributes.remove(xattr_key)                    
                else:
                    attributes[xattr_key] = new_field
        # elif not quiet:
        #     if k == '':
        #         print("no simple tags not found")
        #     else:
        #         print("key not found: " + k)

def delete_other_tags(fname, tags, quiet=False, out=sys.stdout, **unused):
    """Delete tags other than the given tags from the xatag managed xattr fields of fname."""
    tags = tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    # We have to be careful here, because we're iterating over every xattr,
    # not just those in the xatag namespace.
    for xattr_key in attributes.keys():
        if not is_xatag_xattr_key(xattr_key): continue
        k = xattr_to_xatag_key(xattr_key)
        if k not in tags.keys():
            attributes.remove(xattr_key)
        else:
            current_field = attributes[xattr_key]
            vlist = tags[k]
            new_field = remove_tag_values_from_xattr_value(current_field, vlist, complement=True)
            if new_field == '': 
                if not quiet: out.write("removing empty tag key:" + k + "\n")
                attributes.remove(xattr_key)                    
            else:
                attributes[xattr_key] = new_field
                
def delete_all_tags(fname, **unused):
    """Delete all xatag managed xattr fields of fname."""
    attributes = xattr.xattr(fname)
    for key in attributes: 
        if is_xatag_xattr_key(key): attributes.remove(key)

def print_file_tags(fname, tags=False, subset=False, complement=False,
                    terse=False, quiet=False,  
                    longest_filename=0, fsep=":", ksep=':', vsep=' ', 
                    one_line=False, key_val_pairs=False, 
                    out=sys.stdout, **unused):
    # It's a little funny having this check here, but the alternative is
    # having it in every function that calls this one.  Also, maybe in the
    # future quiet will do something else.
    if quiet: return
    padding = max(1, longest_filename - len(fname) + 1)
    prefix = fname + fsep + " "*padding
    tag_dict = read_tags_as_dict(fname)
    if subset:
        tag_dict = subsetted_tags(tag_dict, tags, complement=complement)
    elif terse:
        tags = tag_list_to_dict(tags)
        if complement:
            just_tag_keys_dict = {k:'' for k in tag_dict if k not in tags}
        else:
            just_tag_keys_dict = {k:'' for k in tags}
        tag_dict = subsetted_tags(tag_dict, just_tag_keys_dict, complement=complement)
    print_tag_dict(tag_dict, prefix=prefix, fsep=fsep, ksep=ksep, vsep=vsep, 
                   one_line=one_line, key_val_pairs=key_val_pairs, out=out)

def subsetted_tags(source_tags, tags=False, complement=False, **unused):
    if tags:
        tags = tag_list_to_dict(tags)
        if complement:
            source_tags = subtract_tags(source_tags, tags)
        else:
            source_tags = select_tags(source_tags, tags)
    return source_tags

def copy_tags(source_tags, destination, tags=False, complement=False, 
              **unused):
    """Copy tags in dict souce_tags to each file in destinations."""
    source_tags = subsetted_tags(source_tags, tags, complement=complement)
    new_tags = merge_tags(source_tags, read_tags_as_dict(destination))
    set_tags(destination, new_tags)

def copy_tags_over(source_tags, destination, tags=False, complement=False, **unused):
     """Copy xatag managed xattr fields, removing all other tags."""
     delete_all_tags(destination)
     copy_tags(source_tags, destination, tags, complement)

