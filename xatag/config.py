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


import os
import StringIO
import sys
import re

from xatag.warn import warn
import xatag.constants as constants
import xatag.tag_dict as xtd


def create_config_dir(config_dir=None):
    config_dir = guess_config_dir(config_dir=None)
    # check that the directory doesn't exist or is empty
    if os.path.isdir(config_dir) and os.listdir(config_dir):
        warn("xatag config dir already exists: " + config_dir)
    else:
        if not os.path.isdir(config_dir):
            try:
                os.mkdir(config_dir)
                print "config dir created at: " + config_dir
            except:
                warn("cannot make xatag config dir: " + config_dir)
        else:
            print "using path as config dir: " + config_dir

        known_tags_file = os.path.join(config_dir, constants.KNOWN_TAGS_FILE)
        try:
            with open(known_tags_file, 'w') as f:
                f.write(constants.DEFAULT_KNOWN_TAGS_FILE)
        except:
            warn("cannot make known_tags file: " + known_tags_file)

        recoll_dir = os.path.join(config_dir, constants.RECOLL_CONFIG_DIR)
        try:
            os.mkdir(recoll_dir)
        except:
            warn("cannot make xatag recoll config: " + recoll_dir)

        recoll_conf = os.path.join(recoll_dir, 'recoll.conf')
        recoll_fields = os.path.join(recoll_dir, 'fields')
        try:
            with open(recoll_conf, 'w') as f:
                f.write(constants.DEFAULT_RECOLL_CONF)
            with open(recoll_fields, 'w') as f:
                f.write(form_recoll_fields_file(
                        "xa:tags = XYXATAGS",
                        "xa:tags="))
        except:
            warn("error writing file in xatag recoll config: " + recoll_dir)


def form_recoll_fields_file(prefixes, stored):
    fields = ''
    fields += constants.RECOLL_FIELDS_HEAD
    fields += constants.RECOLL_FIELDS_PREFIXES
    fields += prefixes + '\n'
    fields += constants.RECOLL_FIELDS_STORED
    fields += stored + '\n'
    return fields


def guess_config_dir(config_dir=None):
    if config_dir:
        config_dir = os.path.expanduser(config_dir)
        guess = config_dir
    else:
        envvar = os.environ.get(constants.CONFIG_DIR_VAR)
        if envvar:
            envvar = os.path.expanduser(envvar)
            envvar = os.path.expandvars(envvar)
            guess = envvar
        else:
            guess = os.path.expanduser(constants.DEFAULT_CONFIG_DIR)
    return guess


def guess_recoll_base_config_dir():
    envvar = os.environ.get(constants.RECOLL_BASE_CONFIG_DIR_VAR)
    if envvar:
        envvar = os.path.expanduser(envvar)
        envvar = os.path.expandvars(envvar)
        guess = envvar
    else:
        guess = os.path.expanduser(constants.DEFAULT_RECOLL_BASE_CONFIG_DIR)
    return guess


def get_recoll_base_config_dir():
    guess = guess_recoll_base_config_dir()
    if os.path.isdir(guess):
        return guess
    else:
        warn("recoll base config dir cannot be found: " + guess)
        return None


def get_config_dir(config_dir=None):
    guess = guess_config_dir(config_dir=config_dir)
    if os.path.isdir(guess):
        return guess
    else:
        warn("xatag config dir cannot be found: " + guess)
        warn("run 'xatag --new-config [PATH]' to create it.")
        warn("")
        return None


def get_recoll_fields_file(config_dir=None):
    config_dir = get_config_dir(config_dir=config_dir)
    if not config_dir:
        return None
    fname = os.path.join(config_dir, constants.RECOLL_CONFIG_DIR, 'fields')
    if not os.path.isfile(fname):
        warn("xatag-specific recoll fields file cannot be found: " + fname)
        return None
    return fname


def get_known_tags_file(config_dir=None):
    config_dir = get_config_dir(config_dir=config_dir)
    if not config_dir:
        return None
    fname = os.path.join(config_dir, constants.KNOWN_TAGS_FILE)
    if not os.path.isfile(fname):
        warn("xatag known_tags file cannot be found: " + fname)
        return None
    return fname


def load_known_tags(config_dir=None):
    fname = get_known_tags_file(config_dir)
    if not fname:
        return None
    try:
        with open(fname) as f:
            lines = f.readlines()
    except:
        warn("xatag known_tags file cannot be read: " + fname)
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


def make_known_tags_string(new_tags):
    new_tag_string = StringIO.StringIO()
    xtd.print_tag_dict(new_tags, vsep='; ',
                       out=new_tag_string)
    new_tag_string = new_tag_string.getvalue()
    return new_tag_string


def add_known_tags(new_tags, config_dir=None):
    new_tag_string = make_known_tags_string(new_tags)
    fname = get_known_tags_file(config_dir)
    if not fname:
        return
    try:
        with open(fname, 'a') as f:
            for tag_line in new_tag_string.splitlines():
                f.write(tag_line + "\n")
    except:
        warn("xatag known_tags file cannot be edited: " + fname)


def check_new_tags(tags, add=False, quiet=False, config_dir=None,
                   **other_args):
    """Warn on stderr about the tags that aren't in the known_tags file.

    If add==True, then issue the warning but then add the tag to the
    known_tags file as well, to prevent future warnings.  Also update the
    Recoll fields config file.
    """

    if 'warn_once' in other_args and other_args['warn_once']:
        add=True

    alltags = xtd.tag_list_to_dict(tags)
    # no sense in adding key with no values
    tags = {}
    for key in alltags:
        vals = [val for val in alltags[key]
                if val is not '']
        if vals:
            tags[key] = vals

    known_tags = load_known_tags(config_dir)
    if known_tags is None:
        known_tags = {}
        add = False
    known_keys = known_tags.keys() + ['']

    new_keys = [key for key in tags.keys()
                if key is not ''
                and key is not 'tags'
                and key not in known_keys]
    new_tags = xtd.subtract_tags(tags, known_tags, empty_means_all=False)

    new_key_string = ', '.join(sorted(new_keys))
    new_tag_string = make_known_tags_string(new_tags)

    if not quiet and new_tag_string:
        if add:
            prefix_str = 'adding new'
        else:
            prefix_str = 'unknown'
        if new_key_string:
            sys.stderr.write(prefix_str + " keys: " + new_key_string + "\n")
        for tag_line in new_tag_string.splitlines():
            sys.stderr.write(prefix_str + " tags: " + tag_line + "\n")

    if add and new_tags:
        add_known_tags(new_tags)

    if add and new_keys:
        update_recoll_fields(known_keys + new_keys)


def update_recoll_fields(known_keys, config_dir=None):
    """Write a new fields file in the xatag Recoll directory."""
    recoll_fields_file = get_recoll_fields_file(config_dir)
    if not recoll_fields_file:
        return
    try:
        with open(recoll_fields_file, 'r') as f:
            i = 0
            for line in f:
                i += 1
                if re.match(constants.RECOLL_FIELDS_UPDATE_RE, line):
                    break
                if i >= 5:
                    return False
    except:
        warn("cannot read the recoll fields file: " + recoll_fields_file)

    prefixes_str = ''
    stored_str = ''
    for key in ['tags'] + sorted(known_keys):
        if key == '':
            continue
        prefixes_str += 'xa:' + key + ' = '
        prefixes_str += 'XYXA' + key.upper().replace(':', '') + '\n'
        stored_str += 'xa:' + key + '=\n'

    try:
        with open(recoll_fields_file, 'w') as f:
            f.write(form_recoll_fields_file(prefixes_str, stored_str))
    except:
        warn("cannot edit the recoll fields file: " + recoll_fields_file)
