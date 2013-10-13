import xatag.constants as constants
import xattr

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
        return [cls(key, v) for v in values.split(constants.XATTR_FIELD_SEPARATOR)]

    def to_string(self):
        """Create a 'key:value' formatted string from a Tag object."""
        if self.key == '' or self.key == 'tags':
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
    if quote==True:
        string = "'" + string + "'" if ' ' in string else string
    return string

