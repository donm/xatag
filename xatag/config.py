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
import string

from xatag.warn import warn
import xatag.constants as constants
import xatag.tag_dict as xtd
import xatag.localrecoll as lrcl


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
        ignored_keys_file = os.path.join(config_dir, constants.IGNORED_KEYS_FILE)
        try:
            with open(known_tags_file, 'w') as f:
                f.write(constants.DEFAULT_KNOWN_TAGS_FILE)
            with open(ignored_keys_file, 'w') as f:
                f.write(constants.DEFAULT_IGNORED_KEYS_FILE)
        except:
            warn("error writing file in xatag config dir: " + config_dir)

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
                key = constants.DEFAULT_TAG_KEY
                f.write(form_recoll_fields_file(
                        lrcl.tag_key_to_recoll_prefix(key) +
                        ' = ' +
                        lrcl.tag_key_to_xapian_key(key),
                        lrcl.tag_key_to_recoll_prefix(key)))
        except:
            warn("error writing file in xatag recoll config dir: " + recoll_dir)


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


def find_recoll_base_config_dir():
    guess = guess_recoll_base_config_dir()
    if os.path.isdir(guess):
        return guess
    else:
        warn("recoll base config dir cannot be found: " + guess)
        return None


def find_config_dir(config_dir=None):
    guess = guess_config_dir(config_dir=config_dir)
    if os.path.isdir(guess):
        return guess
    else:
        warn("xatag config dir cannot be found: " + guess)
        warn("run 'xatag --new-config [PATH]' to create it.")
        warn("")
        return None


def guess_recoll_fields_file(config_dir=None):
    config_dir = find_config_dir(config_dir=config_dir)
    if not config_dir:
        return None
    return os.path.join(config_dir, constants.RECOLL_CONFIG_DIR, 'fields')


def find_recoll_fields_file(config_dir=None):
    fname = guess_recoll_fields_file()
    if not os.path.isfile(fname):
        warn("xatag-specific recoll fields file cannot be found: " + fname)
        return None
    return fname


def find_config_file(fname, config_dir=None):
    config_dir = find_config_dir(config_dir=config_dir)
    if not config_dir:
        return None
    fpath = os.path.join(config_dir, fname)
    if not os.path.isfile(fpath):
        warn("xatag " + fname + " file cannot be found: " + fpath)
        return None
    return fpath


def find_known_tags_file(config_dir=None):
    return find_config_file(constants.KNOWN_TAGS_FILE, config_dir=config_dir)


def find_ignored_keys_file(config_dir=None):
    return find_config_file(constants.IGNORED_KEYS_FILE, config_dir=config_dir)


def load_known_tags(config_dir=None):
    fname = find_known_tags_file(config_dir)
    if not fname:
        return None
    try:
        with open(fname) as f:
            lines = f.readlines()
    except:
        warn("xatag known_tags file cannot be read: " + fname)
        return None
    known_tags = {constants.DEFAULT_TAG_KEY:[]}
    for line in lines:
        line = line.strip()
        if line[0] == '#' or line == '':
            continue
        kv = line.split(':')
        if kv == ['']:
            continue
        elif len(kv) == 1:
            key = constants.DEFAULT_TAG_KEY
            vals = kv[0].split(';')
        else:
            key = (':').join(kv[0:-1]).strip()
            vals = kv[-1].split(';')
        for val in vals:
            if key in known_tags:
                known_tags[key].append(val.strip())
            else:
                known_tags[key] = [val.strip()]
    return known_tags


def load_ignored_keys(config_dir=None):
    fname = find_ignored_keys_file(config_dir)
    if not fname:
        return None
    try:
        with open(fname) as f:
            lines = f.readlines()
    except:
        warn("xatag ignored_keys file cannot be read: " + fname)
        return None
    ignored_keys = set([])
    for line in lines:
        line = line.strip()
        if line[0] == '#' or line == '':
            continue
        ignored_keys.add(line)
    return ignored_keys


def make_known_tags_string(new_tags, key_val_pairs=False):
    new_tag_string = StringIO.StringIO()
    xtd.print_tag_dict(new_tags, vsep='; ',
                       key_val_pairs=key_val_pairs,
                       out=new_tag_string)
    new_tag_string = new_tag_string.getvalue()
    return new_tag_string


def add_known_tags(new_tags, config_dir=None):
    new_tag_string = make_known_tags_string(new_tags, key_val_pairs=True)
    fname = find_known_tags_file(config_dir)
    if not fname:
        return
    try:
        with open(fname, 'a') as f:
            for tag_line in new_tag_string.splitlines():
                f.write(tag_line + "\n")
    except:
        warn("xatag known_tags file cannot be edited: " + fname)


def form_recoll_fields_file(prefixes, stored):
    fields = ''
    fields += constants.RECOLL_FIELDS_HEAD
    fields += constants.RECOLL_FIELDS_PREFIXES
    fields += prefixes + '\n'
    fields += constants.RECOLL_FIELDS_STORED
    fields += stored + '\n'
    return fields


def update_recoll_fields(known_keys=False, ignored_keys=False, config_dir=None):
    """Write a new fields file in the xatag Recoll directory.

    known_keys and ignored_keys must be iterable, but can be a tag dict.
    """

    recoll_fields_file = find_recoll_fields_file(config_dir)
    if not recoll_fields_file:
        recoll_fields_file = guess_recoll_fields_file()
        warn("writing " + recoll_fields_file)
    else:
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
            return

    if known_keys is False:
        known_keys = load_known_tags() or []

    if ignored_keys is False:
        ignored_keys = load_ignored_keys() or []
    print ignored_keys
    prefixes_str = ''
    stored_str = ''

    keys = set(known_keys)
    keys = {x for x in keys if x not in ignored_keys}
    keys.add(constants.DEFAULT_TAG_KEY)
    for key in sorted(keys):
        prefixes_str += lrcl.tag_key_to_recoll_prefix(key) + ' = '
        prefixes_str += lrcl.tag_key_to_xapian_key(key) + '\n'
        stored_str += lrcl.tag_key_to_recoll_prefix(key) + '=\n'

    try:
        with open(recoll_fields_file, 'w') as f:
            f.write(form_recoll_fields_file(prefixes_str, stored_str))
    except:
        warn("cannot edit the recoll fields file: " + recoll_fields_file)
