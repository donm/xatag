#pylint: disable-all
import pytest
import xattr

import xatag.attributes as attr
from xatag.operations import *
from xatag.constants import DEFAULT_TAG_KEY
import xatag.constants as constants
import xatag.config as config

NON_XATAG_TAGS = {'user.other.tag':  'something'}
XATAG_TAGS = {
    'user.org.xatag.tags.' + DEFAULT_TAG_KEY: 'tag1;tag2;tag3;tag4;tag5',
    'user.org.xatag.tags.genre': 'indie;pop',
    'user.org.xatag.tags.artist': 'The XX'
    }


@pytest.fixture
def confdir(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    config.create_config_dir()
    fname = tmpdir.join('known_tags')
    with fname.open('a') as f:
        f.write(DEFAULT_TAG_KEY + ": tag1; tag2\n")
        f.write("tag4 ; tag3\n")
        f.write("  key1  : val1   ;  val2  \n")

    fname = tmpdir.join('ignored_keys')
    with fname.open('w') as f:
        f.write("whatever")

    return tmpdir


@pytest.fixture
def file_with_tags(tmpdir):
    f = tmpdir.join('test.txt')
    path = str(f.dirpath() + '/test.txt')
    f.open('a').close
    x = xattr.xattr(path)
    for k, v in NON_XATAG_TAGS.items():
        x[k] = v
    for k, v in XATAG_TAGS.items():
        x[k] = v
    return path


@pytest.fixture
def file_with_tags2(tmpdir):
    tags = {'user.org.xatag.tags.' + DEFAULT_TAG_KEY: 'tag1;tag6',
            'user.org.xatag.tags.genre': 'good',
            'user.org.xatag.tags.other': 'yes'}

    f = tmpdir.join('test2.txt')
    path = str(f.dirpath() + '/test2.txt')
    f.open('a').close
    x = xattr.xattr(path)
    for k, v in tags.items():
        x[k] = v
    return path


def test_add_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    add_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'),
                              Tag('genre', 'awesome'), Tag('artist', '')])
    assert (x['user.org.xatag.tags.' + DEFAULT_TAG_KEY]
            == 'another;tag1;tag2;tag3;tag4;tag5;zanother')
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'awesome;indie;pop'
    add_tags(file_with_tags, [Tag('unused', '')])
    assert 'user.org.xatag.tags.unused' not in x.keys()
    assert 'unused' not in attr.read_tags_as_dict(file_with_tags)


def test_set_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    set_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'),
                              Tag('genre', 'awesome')])
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'another;zanother'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    set_tags(file_with_tags, [Tag('artist', '')])
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'another;zanother'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    assert 'user.org.xatag.tags.artist' not in x.keys()


def test_set_all_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    set_all_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'),
                                  Tag('genre', 'awesome')])
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'another;zanother'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    assert 'user.org.xatag.tags.artist' not in x.keys()


def test_delete_these_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)

    delete_tags(file_with_tags, [Tag('', 'tag4')])
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'tag1;tag2;tag3;tag5'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'indie;pop'

    delete_tags(file_with_tags, [Tag('', t) for t in ['tag2','tag4','tag5']])
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'tag1;tag3'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'indie;pop'

    delete_tags(file_with_tags, Tag('notakey', 'tag'))

    delete_tags(file_with_tags, Tag('genre', 'pop'))
    assert x['user.org.xatag.tags.genre'] == 'indie'
    # xattr fields get deleted explicitly...
    assert 'user.org.xatag.tags.genre' in x.keys()
    delete_tags(file_with_tags, Tag('genre', ''))
    assert 'user.org.xatag.tags.genre' not in x.keys()
    # ...or by removing all of the tag values from the field
    assert 'user.org.xatag.tags.artist' in x.keys()
    assert 'user.org.xatag.tags.' + DEFAULT_TAG_KEY in x.keys()
    delete_tags(file_with_tags, [Tag('', t) for t in ['tag1','tag3']])
    delete_tags(file_with_tags, Tag('artist', 'The XX'))
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert 'user.org.xatag.tags.' + DEFAULT_TAG_KEY not in x.keys()


def test_delete_other_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)

    delete_other_tags(file_with_tags, [Tag('', 'tag4'), Tag('genre', '')])
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert x['user.org.xatag.tags.' + DEFAULT_TAG_KEY] == 'tag4'
    assert x['user.org.xatag.tags.genre'] == 'indie;pop'

    delete_other_tags(file_with_tags, [Tag('', 'tag3'), Tag('genre', 'indie')])
    assert x['user.org.xatag.tags.genre'] == 'indie'
    assert 'user.org.xatag.tags.' + DEFAULT_TAG_KEY not in x.keys()

    delete_other_tags(file_with_tags, Tag('notakey', 'tag'))
    assert 'user.org.xatag.tags.genre' not in x.keys()


def test_delete_all_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    delete_all_tags(file_with_tags)
    assert 'user.org.xatag.tags.' + DEFAULT_TAG_KEY not in x.keys()
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert 'user.org.xatag.tags.genre' not in x.keys()
    assert x['user.other.tag'] == 'something'


def test_copy_tags(file_with_tags, file_with_tags2):
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags(source_tags, file_with_tags2)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert set(d2[DEFAULT_TAG_KEY]) == set(['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'])
    assert set(d2['genre']) == set(['indie', 'pop', 'good'])
    assert set(d2['artist']) == set(['The XX'])
    assert set(d2['other']) == set(['yes'])


def test_copy_tags2(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags(source_tags, file_with_tags2, tags=tags)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert set(d2[DEFAULT_TAG_KEY]) == set(['tag1', 'tag2', 'tag6'])
    assert set(d2['genre']) == set(['indie', 'pop', 'good'])
    assert 'artist' not in d2.keys()
    assert set(d2['other']) == set(['yes'])


def test_copy_tags3(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags(source_tags, file_with_tags2, tags=tags, complement=True)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert set(d2[DEFAULT_TAG_KEY]) == set(['tag1', 'tag3', 'tag4', 'tag5', 'tag6'])
    assert set(d2['genre']) == set(['good'])
    assert set(d2['artist']) == set(['The XX'])
    assert set(d2['other']) == set(['yes'])


def test_copy_tags_over(file_with_tags, file_with_tags2):
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags_over(source_tags, file_with_tags2)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert d1a == d2


def test_copy_tags_over2(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags_over(source_tags, file_with_tags2, tags=tags)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert set(d2[DEFAULT_TAG_KEY]) == set(['tag2'])
    assert set(d2['genre']) == set(['indie', 'pop'])
    assert 'artist' not in d2.keys()
    assert 'other' not in d2.keys()


def test_copy_tags_over3(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = attr.read_tags_as_dict(file_with_tags)
    source_tags = attr.read_tags_as_dict(file_with_tags)
    copy_tags_over(source_tags, file_with_tags2, tags=tags, complement=True)
    d1b = attr.read_tags_as_dict(file_with_tags)
    d2 = attr.read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert set(d2[DEFAULT_TAG_KEY]) == set(['tag1', 'tag3', 'tag4', 'tag5'])
    assert 'genre' not in d2.keys()
    assert set(d2['artist']) == set(['The XX'])
    assert 'other' not in d2.keys()


def test_print_known_tags(confdir, capsys):
    print_known_tags()
    out, err = capsys.readouterr()
    print out
    assert out == """tag:  tag1 tag2 tag3 tag4
key1: val1 val2
"""

def test_check_new_tags(capsys, confdir):
    tags = {DEFAULT_TAG_KEY: [''], DEFAULT_TAG_KEY:[''], 'key': ['']}
    check_new_tags(tags)
    out, err = capsys.readouterr()
    print err
    assert err=="""unknown keys: key
unknown tags: key: \n"""

    tags = {DEFAULT_TAG_KEY: ['tag1', 'tag8', '', 'tag9'],
            'key1': ['val9', ''],
            'key9': ['newval']}
    check_new_tags(tags)
    out, err = capsys.readouterr()
    print out
    print err
    assert err=="""unknown keys: key9
unknown tags: tag: tag8; tag9
unknown tags: key1: val9
unknown tags: key9: newval
"""

    check_new_tags(tags, add=True)
    out, err = capsys.readouterr()
    # kt = load_known_tags()
    print err
    assert err=="""adding new keys: key9
adding new tags: tag: tag8; tag9
adding new tags: key1: val9
adding new tags: key9: newval
"""
    check_new_tags(tags)
    out, err = capsys.readouterr()
    assert err==''

    check_new_tags(tags, config_dir=str(confdir.join('this_doesnt-exist')))
    out, err = capsys.readouterr()
    assert err.startswith('xatag config dir cannot be found')
