import sys
import yaml
import xattr
import os
import collections
from collections import defaultdict
from recoll import recoll

XATTR_PREFIX = 'org.xatag.tags'
XATTR_FIELD_SEPARATOR = ';'

def listify(arg):
    """Make arg iterable, if it's not already.

    I'm sure there's some other iterable object besides a string that you
    would want to listify, but I can't think of them right now.
    """
    if (not isinstance(arg, collections.Iterable)) or isinstance(arg, basestring):
        return [arg]
    else:
        return arg

def is_xatag_xattr_key(name):
    """Check if name starts with XATTR_PREFIX."""
    return name.startswith('user.' + XATTR_PREFIX) or name.startswith(XATTR_PREFIX)

def xatag_to_xattr_key(tag_or_key):
    """Add XATTR_PREFIX to the given string or to the tag's key."""
    try:
        key = tag_or_key.key
    except AttributeError:
        key = tag_or_key
    key = format_tag_key(key)
    if key == '' or key == 'tags':
        return 'user.' + XATTR_PREFIX
    else: 
        return 'user.' + XATTR_PREFIX + '.' + key

def xattr_to_xatag_key(key):
    """Remove XATTR_PREFIX from the given string."""
    key = format_tag_key(key)
    key = key.replace('user.' + XATTR_PREFIX, '')
    key = key.replace(XATTR_PREFIX, '')
    if key != '' and key[0] == '.': key = key[1:]
    return key

def read_tag_keys(fname):
    """Return a list of the xatag keys of the xattr fields in fname in the xatag namespace."""
    attributes = xattr.xattr(fname)
    return [xattr_to_xatag_key(k) for k in attributes if is_xatag_xattr_key(k)]

def read_tags_as_dict(fname):
    """Return a dict of the xattr fields in fname in the xatag namespace."""
    attributes = xattr.xattr(fname)
    # no sense in reading the value if the key isn't going to be chosen
    return {xattr_to_xatag_key(k): xattr_value_to_list(attributes[k])
            for k in attributes if is_xatag_xattr_key(k)}

def write_file_tags(fname, tags):
    """Write the xatag tags to fname."""
    attributes = xattr.xattr(fname)
    
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
    if quote==True:
        string = "'" + string + "'" if ' ' in string else string
    return string

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

def xattr_value_to_list(tag_string):
    """Split the value of a tag xattr and return a list of tag values."""
    return [format_tag_value(x) for x in tag_string.split(XATTR_FIELD_SEPARATOR)
            if format_tag_value(x) != '']

def list_to_xattr_value(tag_list):
    """Return a xattr value that represents the tags in tag_list."""
    return XATTR_FIELD_SEPARATOR.join(sorted(format_tag_value(x) for x in tag_list))

# TODO: optionally print when the tag wasn't there to begin with.  it's
# especially important if you mean
#    -d genre:
# but type
#    -d genre
def remove_tag_values_from_xattr_value(xattr_value, tag_values, complement=False):
    """Remove the values in tag_values from the xattr formatted value."""
    tag_values = listify(tag_values)
    current_values = xattr_value_to_list(xattr_value)
    tag_values_set = set(tag_values)
    if complement:
        if '' in tag_values_set:
            values = current_values
        else:
            values = [value for value in current_values if value in tag_values_set]
    else:
        values = [value for value in current_values if value not in tag_values_set] 
    return list_to_xattr_value(values)

def add_tag_values_to_xattr_value(xattr_value, values_to_add):
    """Add the values in values_to_remove from the xattr formatted value."""
    values_to_add = listify(values_to_add)
    current_values = xattr_value_to_list(xattr_value)
    values = current_values + [value for value in values_to_add if value not in set(current_values)]
    return list_to_xattr_value(values)

class Tag:
    """Simple container for tag key/value pairs."""
    def __init__(self, key, value=''):
        if key == 'tags': key = ''
        self.key = format_tag_key(key)
        self.value = format_tag_value(value)

    @classmethod
    def from_string(cls, tag_str):
        """Create a list of Tag object from a string.

        Where (k,v) denotes Tag(k,v):
            'multi:part:key:value' -> [('multi:part:key', 'value')]
            'simple-tag' -> [('', 'simple-tag')]
            'key:val1;val2;...' -> [('key', 'val1'), ('key', 'val2'), ...]
        """
        parts = tag_str.split(':')
        if len(parts) == 1:
            key = ''
            values = tag_str
        else:
            key = ':'.join(parts[0:-1])
            values = parts[-1]
        return [cls(key, v) for v in values.split(XATTR_FIELD_SEPARATOR)]

    def to_string(self):
        """Create a 'key:value' formatted string from a Tag object."""
        if self.key == '' or self.key == 'tags':
            return self.value
        else:
            return self.key + ":" + self.value
        
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

# TODO: explain why these all have **unused
def add_tags(fname, tags, **unused):
    """Add the given tags from the xatag managed xattr fields of fname."""
    tags = tag_list_to_dict(tags)
    attributes = xattr.xattr(fname)
    for key, value_list in tags.items():
        values_to_add = []
        for v in value_list:
            if v == '':
                print "tag is missing value: " + Tag(key,v).to_string()
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

def delete_tags(fname, tags, complement=False, **unused):
    if complement:
        return delete_other_tags(fname, tags)
    else:
        return delete_these_tags(fname, tags)

def delete_these_tags(fname, tags, **unused):
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
                    print("removing empty tag key:" + k)
                    attributes.remove(xattr_key)                    
                else:
                    attributes[xattr_key] = new_field
        else:
            if k == '':
                print("no simple tags not found")
            else:
                print("key not found: " + k)

def delete_other_tags(fname, tags, **unused):
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
                print("removing empty tag key:" + k)
                attributes.remove(xattr_key)                    
            else:
                attributes[xattr_key] = new_field
                
def delete_all_tags(fname, **unused):
    """Delete all xatag managed xattr fields of fname."""
    attributes = xattr.xattr(fname)
    for key in attributes: 
        if is_xatag_xattr_key(key): attributes.remove(key)

def copy_tags(source, destinations, **unused):
    """Copy all xatag managed xattr fields of fname to each file in destinations."""
    destinations = listify(destinations)
    tags = read_tags_as_dict(source)
    for d in destinations:
        set_tags(d, tags)
