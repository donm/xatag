#pylint: disable-all
import pytest
import re
import xattr

from xatag.cli import *
from xatag.tag import Tag
import xatag.constants as constants

USAGE="""xatag - file tagging using extended attributes (xattr).

Usage:
  xatag [options] ([-a] | -s | -S | -d)      <tag> <file>...
  xatag [options] ([-a] | -s | -S | -d | -l) <file>... -t <tag>...
  xatag [options] ([-a] | -s | -S | -d | -l) <tag>...  -f <file>...
  xatag [options] -l <file>...
  xatag [options] (-c | -C) <src> <dest>... [-t <tag>]...
  xatag [options] -D  <file>...
  xatag [options] -x  <tag>... | <query_string>
  xatag [options] -e  <tag>...
  xatag [options] -m
  xatag  -h | --help
  xatag  -v | --version

File Tagging Commands:
  -a --add          Add all of the TAG(s) to the FILE(s).  This is the
                    default command if you provide more than one argument.
  -l --list         List the tags currently written on FILE(s).
  -s --set          Set the tags of the given FILE(s) to the TAG(s) given, erasing
                    any previous xatag data in the extended attributes in the
                    same fields as new TAG(s).
  -S --set-all      Set the tags of the given FILE(s) to the TAG(s) given, erasing
                    any previous xatag data in the extended attributes.
                    Equivalent to 'xatag -D <file>...; xatag -a <tag> <file>...'
  -d --delete       Remove all of the given TAG(s) to the given FILE(s).
  -D --delete-all   Remove all xatag tags from the FILE(s)
  -c --copy         Copy xatag fields from SRC to DEST(s)
  -C --copy-over    Copy xatag fields from SRC to DEST(s), erasing any
                    previous xatag data in the extended attributes of DEST(s).
                    Equivalent to 'xatag -D <file>...; xatag -c <tag> <file>...'
  -x --execute      Execute a query.

Tag Management Commands:
  -e --enter        Enter TAG into the known tag list.  Adding a tag to
                    the list will prohibit the warning printed when using an
                    unknown tag.  Known tags are also used for shell
                    completion and interactively choosing tags to apply to a
                    file.
  -m --manage       Manage.

Argument Flags:
  -t <tag> --tag=<tag>     The following argument is a tag; when used, all
                           other positional arguments will be considered
                           files.
  -f <file> --file=<file>  The following argument is a file; when used, all
                           other positional arguments will be considered tags.

Genreal Options:
  -n --complement                    The -n stands for "not".  Can be used on -d, -l, and -c/-C.
  -q --quiet                         Be as quiet as possible.
  -T --terse                         Only print values for tag keys that have been altered.
  -F <fsep> --file-separator=<fsep>  [default: :]
  -K <ksep> --key-separator=<ksep>   [default: :]
  -V <vsep> --val-separator=<vsep>   [default:  ] (a space)
  -k --key-val-pairs
  -o --one-line
  -w --no-warn
  -W --warn-once
     --debugging                     Print debugging messages.
  -v --version                       Print version.
  -h --help                          You managed to find this already.


When reading and writing extended attributes, symlinks are followed by default.
"""


@pytest.fixture
def tmpfile(tmpdir):
    other_xattrs = {'user.other.tag':  'something'}
    tags = {
        'user.org.xatag.tags': 'tag1;tag2;two words',
        'user.org.xatag.tags.genre': 'indie;pop',
        'user.org.xatag.tags.artist': 'The XX'
    }

    f = tmpdir.join('test.txt')
    path = str(f.dirpath() + '/test.txt')
    f.open('a').close
    x = xattr.xattr(path)
    for k, v in other_xattrs.items():
        x[k] = v
    for k, v in tags.items():
        x[k] = v
    return path


@pytest.fixture
def tmpfile2(tmpdir):
    tags = {
        'user.org.xatag.tags': 'tag2;tag3',
        'user.org.xatag.tags.genre': 'classical',
    }

    f = tmpdir.join('test2.txt')
    path = str(f.dirpath() + '/test2.txt')
    f.open('a').close
    x = xattr.xattr(path)
    for k, v in tags.items():
        x[k] = v
    return path


def test_parse_tags():
    cli_tags = ["tag", "two words", "key:value", "key2:value1;value2"]
    tags = parse_tags(cli_tags)
    assert tags[0].key == ''
    assert tags[0].value == 'tag'
    assert tags[1].key == ''
    assert tags[1].value == 'two words'
    assert tags[2].key == 'key'
    assert tags[2].value == 'value'
    assert tags[3].key == 'key2'
    assert tags[3].value == 'value1'
    assert tags[4].key == 'key2'
    assert tags[4].value == 'value2'
    assert len(tags) == 5


def test_fix_arguments():
    pass


def test_extract_options():
    arguments = {
        '--opt1': 'a',
        '-opt2': 'b',
        'opt3': 'c',
        '--files': ['f1', 'f2', 'longest'],
        '--destinations': ['f3'],
        }
    options = extract_options(arguments)
    assert options['opt1'] == 'a'
    assert options['opt2'] == 'b'
    assert options['opt3'] == 'c'
    assert options['files'] == ['f1', 'f2', 'longest']
    assert options['longest_filename'] == 7


def test_parse_cli():
    argv=['-a', 'tag', 'f1', 'f2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_add
    assert options['tags'] == [Tag('', 'tag')]
    assert options['files'] == ['f1', 'f2']
    argv=['tag', 'f1', 'f2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_add
    assert options['tags'] == [Tag('', 'tag')]
    assert options['files'] == ['f1', 'f2']
    argv=['f1']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_list
    argv=['-l', 'f1', 'f2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_list
    assert options['files'] == ['f1', 'f2']
    argv=['-S', 'f1', '-t', 'tag', 'f2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_set_all
    assert options['files'] == ['f1', 'f2']
    assert options['tags'] == [Tag('', 'tag')]
    argv=['--set-all', 'f1', '-t', 'tag', 'f2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_set_all
    argv=['-c', 's', '-t', 'tag', 'd1', 'd2']
    command, options = parse_cli(USAGE, argv)
    assert command == cmd_copy
    assert options['tags'] == [Tag('', 'tag')]
    assert options['source'] == 's'
    assert options['destinations'] == ['d1', 'd2']

# These are not unit tests, but this functional testing needs to be done
# anyway and this seems like a fine place to put it.


def standardize_output(out):
    out = re.sub('^.*/', '', out, flags=re.MULTILINE)
    out = re.sub(' +', ' ', out, flags=re.MULTILINE)
    out = re.sub(' $', '', out, flags=re.MULTILINE)
    return out


def compare_output(str1, str2):
    return standardize_output(str1) == standardize_output(str2)


def get_stdout(capsys):
    stdout, stderr = capsys.readouterr()
    stdout=standardize_output(stdout)
    print stdout
    return stdout


def test_cmd_add(tmpfile, tmpfile2, capsys):

    run_cli(USAGE, ['-a', '-T', 'tag4', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-a', 'tag5', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-a', '-q', 'tag6', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-a', 'new key:tag1;tag2', tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    # The output is all lumped together because, though more difficult to read,
    # it's a lot easier to copy and paste.
    gold="""test.txt: tags: tag1 tag2 tag4 'two words'
test2.txt: tags: tag2 tag3 tag4

test.txt: tags: tag1 tag2 tag4 tag5 'two words'
test.txt: artist: 'The XX'
test.txt: genre: indie pop
test2.txt: tags: tag2 tag3 tag4 tag5
test2.txt: genre: classical


test.txt: tags: tag1 tag2 tag4 tag5 tag6 'two words'
test.txt: artist: 'The XX'
test.txt: genre: indie pop
test.txt: new key: tag1 tag2
test2.txt: tags: tag2 tag3 tag4 tag5 tag6
test2.txt: genre: classical
test2.txt: new key: tag1 tag2
"""
    assert compare_output(stdout, gold)


@pytest.fixture
def tmp_known_tags(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    fname = tmpdir.join('known_tags')
    with fname.open('a') as f:
        f.write("tags: tag1; tag2\n")
        f.write("tag3 ; tag\n")
        f.write("  key1  : val1   ;  val2  \n")
    return fname

def test_cmd_add2(tmpfile, tmpfile2, tmp_known_tags, capsys):

    run_cli(USAGE, ['-a', 'tag4', tmpfile])
    run_cli(USAGE, ['-a', '-w', 'tag4', tmpfile])
    run_cli(USAGE, ['-a', '-W', 'tag4', tmpfile])
    run_cli(USAGE, ['-a', 'tag4', tmpfile2])

    stdout, stderr = capsys.readouterr()

    print stdout
    print stderr
    # The output is all lumped together because, though more difficult to read,
    # it's a lot easier to copy and paste.
    gold="""/tmp/pytest-67/test_cmd_add20/test.txt: tags:     tag1 tag2 tag4 'two words'
/tmp/pytest-67/test_cmd_add20/test.txt: artist:   'The XX'
/tmp/pytest-67/test_cmd_add20/test.txt: genre:    indie pop
/tmp/pytest-67/test_cmd_add20/test.txt: tags:     tag1 tag2 tag4 'two words'
/tmp/pytest-67/test_cmd_add20/test.txt: artist:   'The XX'
/tmp/pytest-67/test_cmd_add20/test.txt: genre:    indie pop
/tmp/pytest-67/test_cmd_add20/test.txt: tags:     tag1 tag2 tag4 'two words'
/tmp/pytest-67/test_cmd_add20/test.txt: artist:   'The XX'
/tmp/pytest-67/test_cmd_add20/test.txt: genre:    indie pop
/tmp/pytest-67/test_cmd_add20/test2.txt: tags:     tag2 tag3 tag4
/tmp/pytest-67/test_cmd_add20/test2.txt: genre:    classical
"""
    golderr="""unknown tags: tags:     tag4
adding new tags: tags:     tag4
"""
    assert compare_output(stdout, gold)
    assert compare_output(stderr, golderr)


def test_cmd_list(tmpfile, tmpfile2, capsys):

    run_cli(USAGE, ['-l', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-t', 'genre:', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-nt', 'genre:', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-F:::', '-K::', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-V,', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-k', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-o', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-ko', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', '-ko', '-V,', tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    # The output is all lumped together because, though more difficult to read,
    # it's a lot easier to copy and paste.
    gold="""test.txt: tags: tag1 tag2 'two words'
test.txt: artist: 'The XX'
test.txt: genre: indie pop
test2.txt: tags: tag2 tag3
test2.txt: genre: classical

test.txt: genre: indie pop
test2.txt: genre: classical

test.txt: tags: tag1 tag2 'two words'
test.txt: artist: 'The XX'
test2.txt: tags: tag2 tag3

test.txt::: tags:: tag1 tag2 'two words'
test.txt::: artist:: 'The XX'
test.txt::: genre:: indie pop
test2.txt::: tags:: tag2 tag3
test2.txt::: genre:: classical

test.txt: tags: tag1,tag2,two words
test.txt: artist: The XX
test.txt: genre: indie,pop
test2.txt: tags: tag2,tag3
test2.txt: genre: classical

test.txt: tags: tag1
test.txt: tags: tag2
test.txt: tags: 'two words'
test.txt: artist: 'The XX'
test.txt: genre: indie
test.txt: genre: pop
test2.txt: tags: tag2
test2.txt: tags: tag3
test2.txt: genre: classical

test.txt: tags:"tag1 tag2 'two words'" artist:"'The XX'" genre:"indie pop"
test2.txt: tags:"tag2 tag3" genre:"classical"

test.txt: tags:tag1 tags:tag2 tags:'two words' artist:'The XX' genre:indie genre:pop
test2.txt: tags:tag2 tags:tag3 genre:classical

test.txt: tags:tag1,tags:tag2,tags:two words,artist:The XX,genre:indie,genre:pop
test2.txt: tags:tag2,tags:tag3,genre:classical
"""
    assert compare_output(stdout, gold)


def test_cmd_set(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-s', 'tag', 'genre:awesome', '-f', tmpfile,
                    '-f', tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test.txt: tags: tag
test.txt: artist: 'The XX'
test.txt: genre: awesome
test2.txt: tags: tag
test2.txt: genre: awesome
"""
    assert compare_output(stdout, gold)


def test_cmd_set_all(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-S', 'tag', 'genre:awesome', '-f', tmpfile,
                    '-f', tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test.txt: tags: tag
test.txt: genre: awesome
test2.txt: tags: tag
test2.txt: genre: awesome
"""
    assert compare_output(stdout, gold)


def test_cmd_copy(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-c', tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test2.txt: tags: tag1 tag2 tag3 'two words'
test2.txt: artist: 'The XX'
test2.txt: genre: classical indie pop
"""
    assert compare_output(stdout, gold)


def test_cmd_copy2(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-c', "-t", "tag1", tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-c', "-t", "tags:", tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test2.txt: tags: tag1 tag2 tag3
test2.txt: genre: classical

test2.txt: tags: tag1 tag2 tag3 'two words'
test2.txt: genre: classical
"""
    assert compare_output(stdout, gold)



def test_cmd_copy3(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-c', "-t", ":", tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test2.txt: tags: tag1 tag2 tag3 'two words'
test2.txt: genre: classical
"""
    assert compare_output(stdout, gold)


def test_cmd_copy4(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-c', "-nt", "tag1", tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test2.txt: tags: tag2 tag3 'two words'
test2.txt: artist: 'The XX'
test2.txt: genre: classical indie pop
"""
    assert compare_output(stdout, gold)


def test_cmd_copy_over(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-C', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-C', "-t", "genre:", tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-C', "-nt", "genre:", tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""test2.txt: tags: tag1 tag2 'two words'
test2.txt: artist: 'The XX'
test2.txt: genre: indie pop

test2.txt: genre: indie pop

test2.txt: tags: tag1 tag2 'two words'
test2.txt: artist: 'The XX'
"""
    assert compare_output(stdout, gold)


def test_cmd_delete(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-d', "tag1", tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-d', "-nt", ":", tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-d', "-nt", "two words", tmpfile, tmpfile2])

    stdout = get_stdout(capsys)

    gold="""removing empty tag key:
test.txt: tags: tag2 'two words'
test.txt: artist: 'The XX'
test.txt: genre: indie pop
test2.txt: tags: tag2 tag3
test2.txt: genre: classical

test.txt: tags: tag2 'two words'
test2.txt: tags: tag2 tag3

test.txt: tags: 'two words'
test2.txt:

"""
    assert compare_output(stdout, gold)


def test_cmd_delete(tmpfile, tmpfile2, capsys):
    run_cli(USAGE, ['-D', tmpfile, tmpfile2])
    print
    run_cli(USAGE, ['-l', tmpfile, tmpfile2])
    stdout = get_stdout(capsys)

    gold="\ntest.txt: \ntest2.txt: \n"
    assert compare_output(stdout, gold)
