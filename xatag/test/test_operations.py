import pytest
import xattr

from xatag.operations import *

NON_XATAG_TAGS = {'user.other.tag':  'something'}
XATAG_TAGS = {
    'user.org.xatag.tags': 'tag1;tag2;tag3;tag4;tag5',
    'user.org.xatag.tags.genre': 'indie;pop',
    'user.org.xatag.tags.artist': 'The XX'
    }

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
    tags = {'user.org.xatag.tags': 'tag1;tag6',
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
    add_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'), Tag('genre', 'awesome'),
                              Tag('artist', '')])
    assert x['user.org.xatag.tags'] == 'another;tag1;tag2;tag3;tag4;tag5;zanother'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'awesome;indie;pop'
    add_tags(file_with_tags, [Tag('unused', '')])
    assert 'user.org.xatag.tags.unused' not in x.keys()
    assert 'unused' not in read_tags_as_dict(file_with_tags)

def test_set_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    set_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'), Tag('genre', 'awesome')])
    assert x['user.org.xatag.tags'] == 'another;zanother'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    set_tags(file_with_tags, [Tag('artist', '')])
    assert x['user.org.xatag.tags'] == 'another;zanother'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    assert 'user.org.xatag.tags.artist' not in x.keys()

def test_set_all_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    set_all_tags(file_with_tags, [Tag('', 'another'), Tag('', 'zanother'), Tag('genre', 'awesome')])
    assert x['user.org.xatag.tags'] == 'another;zanother'
    assert x['user.org.xatag.tags.genre'] == 'awesome'
    assert 'user.org.xatag.tags.artist' not in x.keys()

def test_delete_these_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)

    delete_tags(file_with_tags, [Tag('', 'tag4')])
    assert x['user.org.xatag.tags'] == 'tag1;tag2;tag3;tag5'
    assert x['user.org.xatag.tags.artist'] == 'The XX'
    assert x['user.org.xatag.tags.genre'] == 'indie;pop'

    delete_tags(file_with_tags, [Tag('', t) for t in ['tag2','tag4','tag5']])        
    assert x['user.org.xatag.tags'] == 'tag1;tag3'
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
    assert 'user.org.xatag.tags' in x.keys()
    delete_tags(file_with_tags, [Tag('', t) for t in ['tag1','tag3']])
    delete_tags(file_with_tags, Tag('artist', 'The XX'))
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert 'user.org.xatag.tags' not in x.keys()

def test_delete_other_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)

    delete_other_tags(file_with_tags, [Tag('', 'tag4'), Tag('genre', '')])
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert x['user.org.xatag.tags'] == 'tag4'
    assert x['user.org.xatag.tags.genre'] == 'indie;pop'

    delete_other_tags(file_with_tags, [Tag('', 'tag3'), Tag('genre', 'indie')])
    assert x['user.org.xatag.tags.genre'] == 'indie'
    assert 'user.org.xatag.tags' not in x.keys()

    delete_other_tags(file_with_tags, Tag('notakey', 'tag'))
    assert 'user.org.xatag.tags.genre' not in x.keys()

def test_delete_all_tags(file_with_tags):
    x = xattr.xattr(file_with_tags)
    delete_all_tags(file_with_tags)
    assert 'user.org.xatag.tags.tags' not in x.keys()
    assert 'user.org.xatag.tags.artist' not in x.keys()
    assert 'user.org.xatag.tags.genre' not in x.keys()
    assert x['user.other.tag'] == 'something'

def test_copy_tags(file_with_tags, file_with_tags2):
    d1a = read_tags_as_dict(file_with_tags)
    copy_tags(file_with_tags, file_with_tags2)
    d1b = read_tags_as_dict(file_with_tags)
    d2 = read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert sorted(d2['']) == sorted(['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'])
    assert sorted(d2['genre']) == sorted(['indie', 'pop', 'good'])
    assert sorted(d2['artist']) == sorted(['The XX'])
    assert sorted(d2['other']) == sorted(['yes'])

def test_copy_tags2(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = read_tags_as_dict(file_with_tags)
    copy_tags(file_with_tags, file_with_tags2, tags=tags)
    d1b = read_tags_as_dict(file_with_tags)
    d2 = read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert sorted(d2['']) == sorted(['tag1', 'tag2', 'tag6'])
    assert sorted(d2['genre']) == sorted(['indie', 'pop', 'good'])
    assert 'artist' not in d2.keys()
    assert sorted(d2['other']) == sorted(['yes'])

def test_copy_tags3(file_with_tags, file_with_tags2):
    tags = [Tag('', 'tag2'), Tag('genre', '')]
    d1a = read_tags_as_dict(file_with_tags)
    copy_tags(file_with_tags, file_with_tags2, tags=tags, complement=True)
    d1b = read_tags_as_dict(file_with_tags)
    d2 = read_tags_as_dict(file_with_tags2)
    assert d1a == d1b
    assert sorted(d2['']) == sorted(['tag1', 'tag3', 'tag4', 'tag5', 'tag6'])
    assert sorted(d2['genre']) == sorted(['good'])
    assert sorted(d2['artist']) == sorted(['The XX'])
    assert sorted(d2['other']) == sorted(['yes'])
    
    
