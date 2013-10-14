from docopt import docopt
import os.path
import sys

from xatag.warn import warn
from xatag.tag import Tag
import xatag.operations as op
from xatag.attributes import read_tags_as_dict

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
    "--manage",
    ]


def parse_tags(cli_tags):
    """Return a list of Tags representing the array of tag arguments."""
    # Tag.from_string returns a list, so explode it
    return [t for tag in cli_tags for t in Tag.from_string(tag)]


def fix_arguments(arguments):
    """Make canonical keys, renaming or combining various keys in the dict."""
    # When the user manually specifies that an argument is a file or tag, that
    # goes to a separate key.  Make a new list with the values in both keys.
    files = arguments['--file'] + arguments['<file>']
    tags  = arguments['--tag']  + arguments['<tag>']
    arguments['files'] = files
    arguments['tags']  = parse_tags(tags)
    arguments['source']       = arguments['<src>']
    arguments['destinations'] = arguments['<dest>']
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
        command = ('--add' if arguments['<tag>'] else '--list')
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


def cmd_add(options):
    """Perform the actions corresponding to --add."""
    def per_file(fname):
        op.add_tags(fname, **options)
        op.print_file_tags(fname, **options)
    apply_to_files(per_file, options)


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
    apply_to_files(per_file, options)


def cmd_set_all(options):
    """Perform the actions corresponding to --set-all."""
    def per_file(fname):
        op.set_all_tags(fname, **options)
        op.print_file_tags(fname, **options)
    apply_to_files(per_file, options)


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


def cmd_delete(options):
    """Perform the actions corresponding to --delete."""
    def per_file(fname):
        op.delete_tags(fname, **options)
        op.print_file_tags(fname, **options)
    apply_to_files(per_file, options)


def cmd_delete_all(options):
    """Perform the actions corresponding to --delete-all."""
    def per_file(fname):
        op.delete_all_tags(fname)
    apply_to_files(per_file, options)


def cmd_execute(options):
    """Perform the actions corresponding to --execute."""
    # When parsing an '--execute' call, everything is put in the array for
    # <tag> no matter what.  A single tag is a valid query string, so let's
    # just call any list of arguments with one element a query.
    if options('--execute'):
        if len(options['<tag>']) == 1:
            options['<query_string>'] = options['<tag>']
            options['<tag>'] = []
