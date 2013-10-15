import os
import StringIO
import sys

from xatag.warn import warn
import xatag.constants as constants
import xatag.tag_dict as xtd

def get_config_dir(path=None):
    envvar = os.environ.get(constants.CONFIG_DIR_VAR)
    if envvar:
        envvar = os.path.expanduser(envvar)
        envvar = os.path.expandvars(envvar)
    if path:
        if not os.path.isdir(path):
            attempt = path
            path = None
    elif envvar:
        attempt = envvar
        if os.path.isdir(envvar):
            path = envvar
    else:
        default = os.path.expanduser(constants.DEFAULT_CONFIG_DIR)
        attempt = default
        if os.path.isdir(default):
            path = default

    if not path:
        warn("xatag config dir is missing or cannot be read: " + attempt)
    return path


def get_known_tags_file():
    config_dir = get_config_dir()
    if not config_dir:
        return None
    fname = os.path.join(config_dir, constants.KNOWN_TAGS_FILE)
    if not os.path.isfile(fname):
        warn("xatag known_tags file is missing.")
        return None
    return fname


def load_known_tags():
    fname = get_known_tags_file()
    if not fname:
        return None
    try:
        with open(fname) as f:
            lines = f.readlines()
    except:
        warn("xatag known_tags file cannot be read.")
        return None
    known_tags = {}
    for line in lines:
        if line.strip()[0] == '#' or line.strip() == '':
            continue
        kv = line.split(':')
        if kv == ['']:
            continue
        elif len(kv) == 1:
            key = ''
            vals = kv[0].split(';')
        else:
            key = (':').join(kv[0:-1]).strip()
            vals = kv[-1].split(';')
            if key == 'tags':
                key = ''
        for val in vals:
            if key in known_tags:
                known_tags[key].append(val.strip())
            else:
                known_tags[key] = [val.strip()]
    return known_tags


def add_known_tags(new_tags):
    new_tag_string = make_known_tags_string(new_tags)
    fname = get_known_tags_file()
    if not fname:
        return
    try:
        with open(fname, 'a') as f:
            for tag_line in new_tag_string.splitlines():
                f.write(tag_line + "\n")
    except:
        warn("xatag known_tags file cannot be read.")


def make_known_tags_string(new_tags):
    new_tag_string = StringIO.StringIO()
    xtd.print_tag_dict(new_tags, vsep='; ',
                       out=new_tag_string)
    new_tag_string = new_tag_string.getvalue()
    return new_tag_string


def warn_new_tags(tags, add=False):
    """Warn on stderr about the tags that aren't in the known_tags file.

    If add==True, then issue the warning but then add the tag to the
    known_tags file as well, to prevent future warnings.
    """
    tags = xtd.tag_list_to_dict(tags)
    known_tags = load_known_tags()
    if known_tags is None:
        known_tags = {}
        add = False
    known_keys = known_tags.keys() + ['']
    new_keys = [key for key in tags.keys()
                if key is not '' and key not in known_keys]
    new_tags = xtd.subtract_tags(tags, known_tags)
    new_key_string = ', '.join(sorted(new_keys))
    new_tag_string = make_known_tags_string(new_tags)

    if add:
        prefix_str = 'adding new'
    else:
        prefix_str = 'unknown'

    if new_key_string:
        sys.stderr.write(prefix_str + " keys: " + new_key_string + "\n")
    for tag_line in new_tag_string.splitlines():
        sys.stderr.write(prefix_str + " tags: " + tag_line + "\n")

    if add:
        add_known_tags(new_tags)
