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


from docopt import docopt
import os.path
import sys

from xatag.warn import warn
from xatag.tag import Tag
import xatag.operations as op
from xatag.attributes import read_tags_as_dict
import xatag.config as config

COMMAND_LIST = [
    "--add",
    "--interactive",
    "--list",
    "--set",
    "--set-all",
    "--delete",
    "--delete-all",
    "--probe",
    "--copy",
    "--copy-over",
    "--execute",
    "--enter",
    "--new-config",
    "--recoll-tags",
    ]


def parse_tags(cli_tags):
    """Return a list of Tags representing the array of tag arguments."""
    # Tag.from_string returns a list, so explode it
    return [t for tag in cli_tags for t in Tag.from_string(tag)]


def fix_arguments(arguments):
    """Make canonical keys, renaming or combining various keys in the dict."""
    # When the user manually specifies that an argument is a file or tag, that
    # goes to a separate key.  Make a new list with the values in both keys.
    files = arguments['--file'] + arguments['FILE']
    tags  = arguments['--tag']  + arguments['TAG']
    arguments['files'] = files
    arguments['tags']  = parse_tags(tags)
    arguments['source']       = arguments['SRC']
    arguments['destinations'] = arguments['DEST']
    arguments['config_dir'] = arguments['CONFIG_DIR']
    arguments['fsep'] = arguments['--file-separator']
    arguments['ksep'] = arguments['--key-separator']
    arguments['vsep'] = arguments['--val-separator']


def extract_options(arguments):
    """Make an options dict for passing to the cmd functions."""
    options = {}
    for key, val in arguments.items():
        if not key in COMMAND_LIST:
            if key.startswith('--'):
                newkey = key[2:]
            elif key.startswith('-'):
                newkey = key[1:]
            else:
                newkey = key
            newkey = newkey.replace('-', '_')
            options[newkey] = val

    if options['quiet']:
        options['no_warn'] = True

    files_to_print = options['files'] + options['destinations']
    if files_to_print and not ('longest_filename' in options):
        options['longest_filename'] = max(len(f) for f in files_to_print)
    return options


def parse_cli(usage, argv=None):
    """Parse ARGV using the usage docstring."""
    arguments = docopt(usage, argv=argv, version='xatag version 0.0.0')
    fix_arguments(arguments)
    # The command to run is the key in arguments dict with a true value, where
    # that key is also in COMMAND_LIST.
    commands = [k for k in arguments.keys()
                if k in COMMAND_LIST and arguments[k]]
    # Hopefully the user only specified one, and if not then docopt probably
    # caught it.  But just in case...
    if len(commands) > 1:
        sys.exit("Multiple commands specified: " +
                 ','.join(commands))
    if len(commands) == 0:
        command = ('--add' if arguments['TAG'] else '--list')
    else:
        command = commands[0]
    # This works because of convention.  '--some-name' is sent to
    # 'cmd_some_name', which is called with the arguments array.
    command = globals()["cmd_" + command[2:].replace('-', '_')]
    options = extract_options(arguments)
    return (command, options)


def run_cli(usage, argv=None):
    """Parse ARGV and run what was specified."""
    command, options = parse_cli(usage, argv=argv)
    command(options)


def apply_to_files(fun, options, files=False):
    """Call fun on files or options['files'], with error checking."""
    if not files:
        files = options['files']
    for fname in files:
        if os.path.exists(fname):
            try:
                fun(fname)
            except IOError:
                warn("could not write extended attributes: " + fname)
            # xattr throws this when trying to reference an attribute that
            # exists if the file isn't readable
            except KeyError:
                warn("could not read extended attributes: " + fname)
        else:
            warn("path does not exist: " + fname)


def _maybe_check_new_tags(options):
    if not options['no_warn'] or options['warn_once']:
        config.check_new_tags(**options)


def cmd_add(options):
    """Perform the actions corresponding to --add."""
    def per_file(fname):
        op.add_tags(fname, **options)
        op.print_file_tags(fname, **options)
    _maybe_check_new_tags(options)
    apply_to_files(per_file, options)
    op.update_recoll_index(**options)


def cmd_list(options):
    """Perform the actions corresponding to --list."""
    def per_file(fname):
        op.print_file_tags(fname, subset=True, **options)
    options['quiet'] = False
    apply_to_files(per_file, options)


def cmd_set(options):
    """Perform the actions corresponding to --set."""
    def per_file(fname):
        op.set_tags(fname, **options)
        op.print_file_tags(fname, **options)
    _maybe_check_new_tags(options)
    apply_to_files(per_file, options)
    op.update_recoll_index(**options)


def cmd_set_all(options):
    """Perform the actions corresponding to --set-all."""
    def per_file(fname):
        op.set_all_tags(fname, **options)
        op.print_file_tags(fname, **options)
    _maybe_check_new_tags(options)
    apply_to_files(per_file, options)
    op.update_recoll_index(**options)


def validate_source_and_destinations(options):
    """Check that the source and each destination exists.

    If a particular destination doesn't exist, then print a warning but run on
    the remaining destinations.
    """
    source = options['source']
    destinations = []
    for dest in options['destinations']:
        if os.path.exists(dest):
            destinations.append(dest)
        else:
            warn("destination path does not exist: " + dest)
    if not os.path.exists(source):
        source = False
        warn("source path does not exist: " + source)
    options['source'] = source
    options['destinations'] = destinations


def try_read_tags_as_dict(source):
    """Call read_tags_as_dict, exiting on an exception."""
    try:
        source_tags = read_tags_as_dict(source)
    except:
        sys.exit("could not read extended attributes: " + source)
    return source_tags


def cmd_copy(options):
    """Perform the actions corresponding to --copy."""
    def per_file(dest):
        op.copy_tags(source_tags, dest, **options)
        op.print_file_tags(dest, **options)
    validate_source_and_destinations(options)
    source = options['source']
    destinations = options['destinations']
    if source:
        source_tags = try_read_tags_as_dict(source)
        source_tags = op.subsetted_tags(source_tags, **options)
        # remove 'tag' from the options dict so that copy_tags() doesn't try
        # to repeat the subsetting on source_tags
        options['tags'] = []
        apply_to_files(per_file, options, files=destinations)
    op.update_recoll_index(**options)


def cmd_copy_over(options):
    """Perform the actions corresponding to --copy-over."""
    def per_file(dest):
        op.copy_tags_over(source_tags, dest, **options)
        op.print_file_tags(dest, **options)
    validate_source_and_destinations(options)
    source = options['source']
    destinations = options['destinations']
    if source:
        source_tags = try_read_tags_as_dict(source)
        source_tags = op.subsetted_tags(source_tags, **options)
        # remove 'tag' from the options dict so that copy_tags() doesn't try
        # to repeat the subsetting on source_tags
        options['tags'] = []
        apply_to_files(per_file, options, files=destinations)
    op.update_recoll_index(**options)


def cmd_delete(options):
    """Perform the actions corresponding to --delete."""
    def per_file(fname):
        op.delete_tags(fname, **options)
        op.print_file_tags(fname, **options)
    apply_to_files(per_file, options)
    op.update_recoll_index(**options)


def cmd_delete_all(options):
    """Perform the actions corresponding to --delete-all."""
    def per_file(fname):
        op.delete_all_tags(fname)
    apply_to_files(per_file, options)
    op.update_recoll_index(**options)


def cmd_execute(options):
    """Perform the actions corresponding to --execute."""
    # When parsing an '--execute' call, everything is put in the array for
    # TAG no matter what.  A single tag is a valid query string, so let's
    # just call any list of arguments with one element a query.
    if len(options['TAG']) == 1:
        options['QUERY_STRING'] = options['TAG']
        options['TAG'] = []
    warn('the execute command is not implemented yet')


def cmd_enter(options):
    """Add tags to the known_tags file."""
    # Well, that was easy.
    config.check_new_tags(add=True, **options)


def cmd_new_config(options):
    """Create a new config directory at path, or a default location."""
    config.create_config_dir(options['config_dir'])


def cmd_recoll_tags(options):
    """Create a new config directory at path, or a default location."""
    op.print_file_tags(options['files'][0], for_recoll=True, **options)
