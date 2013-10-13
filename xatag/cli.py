from docopt import docopt
import os.path

from xatag.warn import warn
from xatag.operations import *

command_list = [
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
    # Tag.from_string returns a list, so explode it
    return [t for tag in cli_tags for t in Tag.from_string(tag)]

def fix_arguments(arguments):
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
    for key,val in arguments.items():
        if not key in command_list:
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
    arguments = docopt(usage, argv=argv, version='xatag version 0.0.0')
    fix_arguments(arguments)
    command = False
    for c in command_list:
        if c in arguments.keys() and arguments[c]: 
            command = c
            break
    if not command:
        # TODO: test if all the commands are there
        command = ('--add' if arguments['<tag>'] else '--list')
    # This works because of convention.  '--some-name' is sent to
    # 'cmd_some_name', which is called with the arguments array.
    command = globals()["cmd_" + command[2:].replace('-', '_')]
    options = extract_options(arguments)
    return (command, options)

def run_cli(usage, argv=None):
    command, options = parse_cli(usage, argv=argv)
    command(options)

def apply_to_files(fun, options, files=False):
    if not files: files = options['files']
    for f in files:
        if os.path.exists(f):
            try:
                fun(f)
            except IOError:
                warn("could not write extended attributes: " + f)
            # xattr throws this when trying to reference an attribute that
            # exists if the file isn't readable
            except KeyError:
                warn("could not read extended attributes: " + f)
        else:
            warn("path does not exist: " + f)

def cmd_add(options): 
    def per_file(f):
        add_tags(f, **options)
        print_file_tags(f, **options)
    apply_to_files(per_file, options)
                
def cmd_list(options):
    def per_file(f):
        print_file_tags(f, subset=True, **options)
    options['quiet'] = False
    apply_to_files(per_file, options)

def cmd_set(options):
    def per_file(f):
        set_tags(f, **options)
        print_file_tags(f, **options)
    apply_to_files(per_file, options)

def cmd_set_all(options):
    def per_file(f):
        set_all_tags(f, **options)
        print_file_tags(f, **options)
    apply_to_files(per_file, options)

def validate_source_and_destinations(options):
    source = options['source']
    destinations = []
    for d in options['destinations']:
        if os.path.exists(d):
            destinations.append(d)
        else:
            warn("destination path does not exist: " + d)
    if not os.path.exists(source):
        source = False
        warn("source path does not exist: " + source)
    options['source'] = source
    options['destinations'] = destinations

def try_read_tags_as_dict(source):
    try:
        source_tags = read_tags_as_dict(source)
    except:
        sys.exit("could not read extended attributes: " + source)
    return source_tags

def cmd_copy(options):
    def per_file(d):
        copy_tags(source_tags, d, **options)
        print_file_tags(d, **options)
    validate_source_and_destinations(options)
    source = options['source']
    destinations = options['destinations']
    if source:
        source_tags = try_read_tags_as_dict(source)
        source_tags = subsetted_tags(source_tags, **options)
        # remove 'tag' from the options dict so that copy_tags() doesn't try
        # to repeat the subsetting on source_tags
        options['tags'] = []
        apply_to_files(per_file, options, files=destinations)

def cmd_copy_over(options):
    def per_file(d):
        copy_tags_over(source_tags, d, **options)
        print_file_tags(d, **options)
    validate_source_and_destinations(options)
    source = options['source']
    destinations = options['destinations']
    if source:
        source_tags = try_read_tags_as_dict(source)
        source_tags = subsetted_tags(source_tags, **options)
        # remove 'tag' from the options dict so that copy_tags() doesn't try
        # to repeat the subsetting on source_tags
        options['tags'] = []
        apply_to_files(per_file, options, files=destinations)

def cmd_delete(options):
    def per_file(f):
        delete_tags(f, **options)
        print_file_tags(f, **options)
    apply_to_files(per_file, options)
        
def cmd_delete_all(options):
    def per_file(f):
        delete_all_tags(f)
    apply_to_files(per_file, options)

def cmd_execute(options):
    # When parsing an '--execute' call, everything is put in the array for
    # <tag> no matter what.  A single tag is a valid query string, so let's
    # just call any list of arguments with one element a query.
    if options('--execute'):
        if len(options['<tag>']) == 1:
            options['<query_string>'] = options['<tag>']
            options['<tag>'] = []
